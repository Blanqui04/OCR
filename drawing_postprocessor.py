"""
Technical Drawing Post-Processor
Structures OCR data from technical drawings into meaningful information blocks
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import math
from collections import defaultdict

@dataclass
class TechnicalElement:
    """Represents a structured technical element from a drawing"""
    element_number: str
    description: str
    value: str
    tolerance: str
    confidence: float
    position: Tuple[float, float]
    bounding_box: Tuple[float, float, float, float]
    page_number: int

@dataclass
class DrawingBlock:
    """Represents a logical block of related text elements"""
    block_id: str
    elements: List[TechnicalElement]
    block_type: str  # 'dimension', 'annotation', 'title_block', 'parts_list', etc.
    centroid: Tuple[float, float]
    confidence: float

class DrawingPostProcessor:
    def __init__(self):
        # Patterns for technical drawing elements
        self.dimension_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:mm|m|cm|in|"|\′)?',  # Dimensions
            r'R(\d+(?:\.\d+)?)',  # Radius
            r'Ø(\d+(?:\.\d+)?)',  # Diameter
            r'(\d+(?:\.\d+)?)°',  # Angles
        ]
        
        self.tolerance_patterns = [
            r'±\s*(\d+(?:\.\d+)?)',  # Plus/minus tolerance
            r'\+(\d+(?:\.\d+)?)\s*-(\d+(?:\.\d+)?)',  # Plus/minus tolerance
            r'H\d+|h\d+|IT\d+',  # ISO tolerance grades
            r'(\d+(?:\.\d+)?)\s*±\s*(\d+(?:\.\d+)?)',  # Value with tolerance
        ]
        
        self.element_number_patterns = [
            r'^(\d+)\.?$',  # Simple numbers: 1, 2, 3.
            r'^([A-Z]\d*)$',  # Letter-number combinations: A1, B2
            r'^\((\d+)\)$',  # Numbers in parentheses: (1), (2)
        ]
        
        # Grouping parameters
        self.proximity_threshold = 50  # pixels
        self.alignment_threshold = 10  # pixels for vertical/horizontal alignment

    def process_drawing(self, text_blocks: List) -> Dict:
        """
        Main processing function that structures OCR data from technical drawings
        """
        # Convert OCR blocks to our format
        drawing_elements = self._extract_technical_elements(text_blocks)
        
        # Group related elements into logical blocks
        logical_blocks = self._group_elements_into_blocks(drawing_elements)
        
        # Structure the data
        structured_data = self._structure_drawing_data(logical_blocks)
        
        return {
            'technical_elements': drawing_elements,
            'logical_blocks': logical_blocks,
            'structured_data': structured_data,
            'statistics': self._generate_statistics(drawing_elements, logical_blocks)
        }

    def _extract_technical_elements(self, text_blocks: List) -> List[TechnicalElement]:
        """Extract and classify technical elements from OCR text blocks"""
        elements = []
        
        for i, block in enumerate(text_blocks):
            text = block.text.strip()
            if not text:
                continue
                
            # Try to parse as different types of technical elements
            element = self._parse_technical_element(block, i)
            if element:
                elements.append(element)
        
        return elements

    def _parse_technical_element(self, block, index: int) -> Optional[TechnicalElement]:
        """Parse a single text block into a technical element"""
        text = block.text.strip()
        
        # Initialize element components
        element_number = ""
        description = ""
        value = ""
        tolerance = ""
        
        # Try to identify element number
        for pattern in self.element_number_patterns:
            match = re.search(pattern, text)
            if match:
                element_number = match.group(1)
                break
        
        # Extract dimensions and values
        dimension_match = None
        for pattern in self.dimension_patterns:
            match = re.search(pattern, text)
            if match:
                value = match.group(1) if match.group(1) else match.group(0)
                dimension_match = match
                break
        
        # Extract tolerance
        for pattern in self.tolerance_patterns:
            match = re.search(pattern, text)
            if match:
                tolerance = match.group(0)
                break
        
        # If no specific patterns found, treat as description
        if not element_number and not dimension_match and not tolerance:
            description = text
        
        # If we found a dimension but no description, try to extract context
        if dimension_match and not description:
            # Remove the dimension part to get potential description
            remaining_text = text.replace(dimension_match.group(0), "").strip()
            if remaining_text:
                description = remaining_text
        
        return TechnicalElement(
            element_number=element_number,
            description=description,
            value=value,
            tolerance=tolerance,
            confidence=block.confidence,
            position=(block.bbox[0], block.bbox[1]),
            bounding_box=block.bbox,
            page_number=block.page_num
        )

    def _group_elements_into_blocks(self, elements: List[TechnicalElement]) -> List[DrawingBlock]:
        """Group related elements into logical blocks"""
        if not elements:
            return []
        
        # Create groups based on proximity and alignment
        element_groups = self._create_proximity_groups(elements)
        
        # Convert groups to DrawingBlocks
        logical_blocks = []
        for i, group in enumerate(element_groups):
            block_type = self._determine_block_type(group)
            centroid = self._calculate_centroid(group)
            avg_confidence = sum(e.confidence for e in group) / len(group)
            
            logical_blocks.append(DrawingBlock(
                block_id=f"block_{i+1}",
                elements=group,
                block_type=block_type,
                centroid=centroid,
                confidence=avg_confidence
            ))
        
        return logical_blocks

    def _create_proximity_groups(self, elements: List[TechnicalElement]) -> List[List[TechnicalElement]]:
        """Group elements based on proximity and alignment"""
        if not elements:
            return []
        
        # Start with each element in its own group
        groups = [[element] for element in elements]
        
        # Iteratively merge groups that should be together
        merged = True
        while merged:
            merged = False
            new_groups = []
            used_indices = set()
            
            for i, group1 in enumerate(groups):
                if i in used_indices:
                    continue
                    
                merged_group = group1[:]
                used_indices.add(i)
                
                for j, group2 in enumerate(groups):
                    if j <= i or j in used_indices:
                        continue
                    
                    if self._should_merge_groups(group1, group2):
                        merged_group.extend(group2)
                        used_indices.add(j)
                        merged = True
                
                new_groups.append(merged_group)
            
            groups = new_groups
        
        return groups

    def _should_merge_groups(self, group1: List[TechnicalElement], group2: List[TechnicalElement]) -> bool:
        """Determine if two groups should be merged"""
        # Check proximity
        min_distance = float('inf')
        for elem1 in group1:
            for elem2 in group2:
                distance = self._calculate_distance(elem1.position, elem2.position)
                min_distance = min(min_distance, distance)
        
        if min_distance > self.proximity_threshold:
            return False
        
        # Check for logical relationships
        # 1. Element number followed by description/value
        # 2. Value followed by tolerance
        # 3. Aligned elements (same row or column)
        
        # Check alignment
        if self._are_groups_aligned(group1, group2):
            return True
        
        # Check for number-description relationship
        if self._have_number_description_relationship(group1, group2):
            return True
        
        # Check for value-tolerance relationship
        if self._have_value_tolerance_relationship(group1, group2):
            return True
        
        return False

    def _are_groups_aligned(self, group1: List[TechnicalElement], group2: List[TechnicalElement]) -> bool:
        """Check if two groups are vertically or horizontally aligned"""
        centroid1 = self._calculate_centroid(group1)
        centroid2 = self._calculate_centroid(group2)
        
        # Check horizontal alignment (same Y coordinate)
        if abs(centroid1[1] - centroid2[1]) <= self.alignment_threshold:
            return True
        
        # Check vertical alignment (same X coordinate)
        if abs(centroid1[0] - centroid2[0]) <= self.alignment_threshold:
            return True
        
        return False

    def _have_number_description_relationship(self, group1: List[TechnicalElement], group2: List[TechnicalElement]) -> bool:
        """Check if one group has element numbers and the other has descriptions"""
        has_number_1 = any(elem.element_number for elem in group1)
        has_description_2 = any(elem.description for elem in group2)
        
        has_number_2 = any(elem.element_number for elem in group2)
        has_description_1 = any(elem.description for elem in group1)
        
        return (has_number_1 and has_description_2) or (has_number_2 and has_description_1)

    def _have_value_tolerance_relationship(self, group1: List[TechnicalElement], group2: List[TechnicalElement]) -> bool:
        """Check if one group has values and the other has tolerances"""
        has_value_1 = any(elem.value for elem in group1)
        has_tolerance_2 = any(elem.tolerance for elem in group2)
        
        has_value_2 = any(elem.value for elem in group2)
        has_tolerance_1 = any(elem.tolerance for elem in group1)
        
        return (has_value_1 and has_tolerance_2) or (has_value_2 and has_tolerance_1)

    def _calculate_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two positions"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def _calculate_centroid(self, elements: List[TechnicalElement]) -> Tuple[float, float]:
        """Calculate the centroid of a group of elements"""
        if not elements:
            return (0, 0)
        
        x_sum = sum(elem.position[0] for elem in elements)
        y_sum = sum(elem.position[1] for elem in elements)
        
        return (x_sum / len(elements), y_sum / len(elements))

    def _determine_block_type(self, elements: List[TechnicalElement]) -> str:
        """Determine the type of a logical block"""
        # Count different types of content
        has_numbers = any(elem.element_number for elem in elements)
        has_dimensions = any(elem.value for elem in elements)
        has_tolerances = any(elem.tolerance for elem in elements)
        has_descriptions = any(elem.description for elem in elements)
        
        # Classify based on content
        if has_numbers and has_descriptions and has_dimensions:
            return "parts_list"
        elif has_dimensions and has_tolerances:
            return "dimension"
        elif has_numbers and has_descriptions:
            return "annotation"
        elif has_dimensions:
            return "measurement"
        elif has_descriptions and not has_dimensions:
            return "text_annotation"
        else:
            return "unknown"

    def _structure_drawing_data(self, logical_blocks: List[DrawingBlock]) -> Dict:
        """Structure the data into final format"""
        structured_data = {
            'parts_list': [],
            'dimensions': [],
            'annotations': [],
            'measurements': [],
            'title_block': [],
            'other': []
        }
        
        for block in logical_blocks:
            # Merge elements within the block to create structured entries
            merged_elements = self._merge_block_elements(block)
            
            # Categorize by block type
            if block.block_type == "parts_list":
                structured_data['parts_list'].extend(merged_elements)
            elif block.block_type == "dimension":
                structured_data['dimensions'].extend(merged_elements)
            elif block.block_type == "annotation":
                structured_data['annotations'].extend(merged_elements)
            elif block.block_type == "measurement":
                structured_data['measurements'].extend(merged_elements)
            else:
                structured_data['other'].extend(merged_elements)
        
        return structured_data

    def _merge_block_elements(self, block: DrawingBlock) -> List[Dict]:
        """Merge elements within a block into structured entries"""
        merged_entries = []
        
        # Group elements by their element numbers or proximity
        element_groups = defaultdict(list)
        
        for element in block.elements:
            if element.element_number:
                key = element.element_number
            else:
                # Group by position for elements without numbers
                key = f"pos_{int(element.position[0]/50)}_{int(element.position[1]/50)}"
            
            element_groups[key].append(element)
        
        # Create merged entries
        for group_key, group_elements in element_groups.items():
            merged_entry = {
                'element_number': '',
                'description': '',
                'value': '',
                'tolerance': '',
                'confidence': 0.0,
                'position': (0, 0),
                'block_id': block.block_id,
                'block_type': block.block_type
            }
            
            # Merge information from all elements in the group
            descriptions = []
            values = []
            tolerances = []
            confidences = []
            positions = []
            
            for element in group_elements:
                if element.element_number:
                    merged_entry['element_number'] = element.element_number
                if element.description:
                    descriptions.append(element.description)
                if element.value:
                    values.append(element.value)
                if element.tolerance:
                    tolerances.append(element.tolerance)
                
                confidences.append(element.confidence)
                positions.append(element.position)
            
            # Combine the information
            merged_entry['description'] = ' | '.join(descriptions) if descriptions else ''
            merged_entry['value'] = ' | '.join(values) if values else ''
            merged_entry['tolerance'] = ' | '.join(tolerances) if tolerances else ''
            merged_entry['confidence'] = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Calculate average position
            if positions:
                avg_x = sum(pos[0] for pos in positions) / len(positions)
                avg_y = sum(pos[1] for pos in positions) / len(positions)
                merged_entry['position'] = (avg_x, avg_y)
            
            merged_entries.append(merged_entry)
        
        return merged_entries

    def _generate_statistics(self, elements: List[TechnicalElement], blocks: List[DrawingBlock]) -> Dict:
        """Generate statistics about the processed drawing"""
        stats = {
            'total_elements': len(elements),
            'total_blocks': len(blocks),
            'elements_with_numbers': len([e for e in elements if e.element_number]),
            'elements_with_values': len([e for e in elements if e.value]),
            'elements_with_tolerances': len([e for e in elements if e.tolerance]),
            'elements_with_descriptions': len([e for e in elements if e.description]),
            'block_types': {},
            'average_confidence': 0.0
        }
        
        # Count block types
        for block in blocks:
            stats['block_types'][block.block_type] = stats['block_types'].get(block.block_type, 0) + 1
        
        # Calculate average confidence
        if elements:
            stats['average_confidence'] = sum(e.confidence for e in elements) / len(elements)
        
        return stats

    def export_structured_data(self, structured_data: Dict, format: str = 'csv') -> str:
        """Export structured data in various formats"""
        if format.lower() == 'csv':
            return self._export_to_csv(structured_data)
        elif format.lower() == 'json':
            return self._export_to_json(structured_data)
        else:
            return str(structured_data)

    def _export_to_csv(self, structured_data: Dict) -> str:
        """Export to CSV format"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Category', 'Element Number', 'Description', 'Value', 'Tolerance', 'Confidence', 'Block Type'])
        
        # Write data for each category
        for category, entries in structured_data.items():
            for entry in entries:
                writer.writerow([
                    category,
                    entry.get('element_number', ''),
                    entry.get('description', ''),
                    entry.get('value', ''),
                    entry.get('tolerance', ''),
                    f"{entry.get('confidence', 0):.2f}",
                    entry.get('block_type', '')
                ])
        
        return output.getvalue()

    def _export_to_json(self, structured_data: Dict) -> str:
        """Export to JSON format"""
        import json
        return json.dumps(structured_data, indent=2, ensure_ascii=False)
