"""
Pipeline d'IA integrat - Actualització del pipeline principal
Modifica el pipeline existent per suportar detecció híbrida amb IA
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Importar el pipeline híbrid
try:
    from src.ai_model.hybrid_pipeline import HybridDetectionPipeline, ContinuousLearningManager
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class AIEnhancedPipeline:
    """
    Pipeline principal amb suport per IA híbrida
    """
    
    def __init__(self, config_path: str):
        """
        Inicialitza el pipeline amb suport d'IA opcional
        
        Args:
            config_path: Path al fitxer de configuració
        """
        self.config_path = Path(config_path)
        self.project_dir = self.config_path.parent
        self.logger = logging.getLogger(__name__)
        
        # Carregar configuració
        self.config = self._load_config()
        
        # Inicialitzar components d'IA si estan disponibles
        self.ai_pipeline = None
        self.learning_manager = None
        
        if AI_AVAILABLE:
            self._initialize_ai_components()
    
    def _load_config(self) -> Dict:
        """Carrega la configuració del pipeline"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            self.logger.error(f"Error carregant configuració: {e}")
            return {}
    
    def _initialize_ai_components(self):
        """Inicialitza components d'IA"""
        try:
            # Path al model d'IA (si existeix)
            model_path = self.config.get("ai_model_path")
            if model_path:
                model_path = self.project_dir / model_path
            
            # Crear pipeline híbrid
            self.ai_pipeline = HybridDetectionPipeline(
                str(self.project_dir), 
                str(model_path) if model_path and model_path.exists() else None
            )
            
            # Crear gestor d'aprenentatge continu
            self.learning_manager = ContinuousLearningManager(str(self.project_dir))
            
            self.logger.info("Components d'IA inicialitzats correctament")
            
        except Exception as e:
            self.logger.error(f"Error inicialitzant IA: {e}")
            self.ai_pipeline = None
            self.learning_manager = None
    
    def process_document_with_ai(self, pdf_path: str, use_ai: bool = True) -> Dict:
        """
        Processa un document amb suport d'IA opcional
        
        Args:
            pdf_path: Path al PDF
            use_ai: Si utilitzar IA o només regles tradicionals
            
        Returns:
            Resultats del processament
        """
        results = {
            "status": "success",
            "pdf_path": pdf_path,
            "pages": [],
            "ai_enabled": use_ai and self.ai_pipeline is not None,
            "total_elements": 0,
            "human_review_required": False
        }
        
        try:
            # 1. Convertir PDF a imatges (component existent)
            from src.pdf_to_images import convert_pdf_to_images
            image_paths = convert_pdf_to_images(pdf_path, str(self.project_dir / "data" / "images"))
            
            # 2. Processar cada pàgina
            for i, image_path in enumerate(image_paths):
                page_results = self._process_single_page(image_path, i + 1, use_ai)
                results["pages"].append(page_results)
                results["total_elements"] += page_results.get("total_elements", 0)
                
                if page_results.get("needs_human_review", False):
                    results["human_review_required"] = True
            
            self.logger.info(f"Document processat: {len(results['pages'])} pàgines, {results['total_elements']} elements")
            
        except Exception as e:
            self.logger.error(f"Error processant document: {e}")
            results["status"] = "error"
            results["error"] = str(e)
        
        return results
    
    def _process_single_page(self, image_path: str, page_num: int, use_ai: bool) -> Dict:
        """
        Processa una sola pàgina amb IA opcional
        
        Args:
            image_path: Path a la imatge de la pàgina
            page_num: Número de pàgina
            use_ai: Si utilitzar IA
            
        Returns:
            Resultats de la pàgina
        """
        page_results = {
            "page_number": page_num,
            "image_path": image_path,
            "ocr_data": [],
            "elements": [],
            "relationships": [],
            "human_review_tasks": [],
            "total_elements": 0,
            "needs_human_review": False,
            "processing_method": "ai_hybrid" if use_ai and self.ai_pipeline else "rules_only"
        }
        
        try:
            # 1. OCR (component existent)
            from src.ocr_processor import process_image_ocr
            ocr_data = process_image_ocr(image_path)
            page_results["ocr_data"] = ocr_data
            
            # 2. Obtenir dimensions de la imatge
            import cv2
            image = cv2.imread(image_path)
            image_shape = image.shape[:2] if image is not None else (1000, 1000)
            
            # 3. Processar amb IA híbrida o només regles
            if use_ai and self.ai_pipeline:
                # Processament híbrid amb IA
                ai_results = self.ai_pipeline.process_image_hybrid(image_path, ocr_data, image_shape)
                
                page_results["elements"] = ai_results["merged_elements"]
                page_results["relationships"] = ai_results["relationships"]
                page_results["human_review_tasks"] = ai_results["human_review_tasks"]
                page_results["needs_human_review"] = len(ai_results["human_review_tasks"]) > 0
                page_results["ai_metadata"] = ai_results["processing_metadata"]
                
            else:
                # Processament tradicional només amb regles
                from src.data_extractor import extract_technical_data
                tech_data = extract_technical_data(ocr_data)
                
                # Convertir a format estàndard
                elements = []
                for dim in tech_data.get("dimensions", []):
                    elements.append({
                        "type": "dimension_text",
                        "bbox": dim.get("bbox", {}),
                        "confidence": 0.8,
                        "text": dim.get("text", ""),
                        "source": "rules"
                    })
                
                page_results["elements"] = elements
                page_results["relationships"] = []
                page_results["human_review_tasks"] = []
            
            page_results["total_elements"] = len(page_results["elements"])
            
        except Exception as e:
            self.logger.error(f"Error processant pàgina {page_num}: {e}")
            page_results["error"] = str(e)
        
        return page_results
    
    def save_user_feedback(self, page_num: int, element_id: str, corrected_type: str, user_id: str = "default"):
        """
        Guarda feedback de l'usuari per aprenentatge continu
        
        Args:
            page_num: Número de pàgina
            element_id: ID de l'element corregit
            corrected_type: Tipus correcte segons l'usuari
            user_id: ID de l'usuari
        """
        if not self.learning_manager:
            self.logger.warning("Gestor d'aprenentatge no disponible")
            return
        
        try:
            # Buscar l'element en els resultats guardats
            # (Aquí hauríem de tenir una manera de recuperar l'element específic)
            element = {
                "page_num": page_num,
                "element_id": element_id,
                "type": "unknown",  # S'hauria de recuperar de l'estat
                "confidence": 0.5
            }
            
            self.learning_manager.save_user_correction(element, corrected_type, user_id)
            self.logger.info(f"Feedback guardat per element {element_id} a pàgina {page_num}")
            
        except Exception as e:
            self.logger.error(f"Error guardant feedback: {e}")
    
    def get_model_performance_stats(self) -> Dict:
        """
        Obté estadístiques de rendiment del model
        
        Returns:
            Estadístiques del model
        """
        stats = {
            "ai_available": self.ai_pipeline is not None,
            "model_loaded": False,
            "total_corrections": 0,
            "accuracy_estimate": 0.0
        }
        
        if self.ai_pipeline and self.ai_pipeline.ai_detector:
            stats["model_loaded"] = True
        
        if self.learning_manager:
            corrections = self.learning_manager.collect_training_data()
            stats["total_corrections"] = len(corrections)
            
            # Calcular precisió estimada basada en correccions
            if len(corrections) > 0:
                # Simplicat: assumir que menys correccions = millor precisió
                stats["accuracy_estimate"] = max(0.5, 1.0 - (len(corrections) / 100))
        
        return stats
    
    def export_results_enhanced(self, results: Dict, output_format: str = "json") -> str:
        """
        Exporta resultats amb informació d'IA inclosa
        
        Args:
            results: Resultats del processament
            output_format: Format d'exportació ('json', 'excel', 'json_schema')
            
        Returns:
            Path al fitxer exportat
        """
        output_dir = self.project_dir / "data" / "output" / "ai_enhanced"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format == "json":
            output_path = output_dir / f"ai_results_{timestamp}.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        elif output_format == "excel":
            import pandas as pd
            from openpyxl import Workbook
            
            output_path = output_dir / f"ai_results_{timestamp}.xlsx"
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Full summary
                summary_data = []
                for page in results.get("pages", []):
                    for elem in page.get("elements", []):
                        summary_data.append({
                            "page": page["page_number"],
                            "type": elem.get("type", ""),
                            "confidence": elem.get("confidence", 0),
                            "source": elem.get("source", ""),
                            "text": elem.get("text", "")
                        })
                
                if summary_data:
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name="Elements", index=False)
                
                # Human review tasks
                review_data = []
                for page in results.get("pages", []):
                    for task in page.get("human_review_tasks", []):
                        review_data.append({
                            "page": page["page_number"],
                            "task_id": task.get("task_id", ""),
                            "confidence": task.get("confidence", 0),
                            "suggested_type": task.get("suggested_type", ""),
                            "question": task.get("review_question", "")
                        })
                
                if review_data:
                    pd.DataFrame(review_data).to_excel(writer, sheet_name="NeedsReview", index=False)
        
        else:  # json_schema
            output_path = output_dir / f"ai_results_schema_{timestamp}.json"
            schema_data = self._convert_to_schema_format(results)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(schema_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Resultats exportats a: {output_path}")
        return str(output_path)
    
    def _convert_to_schema_format(self, results: Dict) -> Dict:
        """Converteix resultats al format de schema JSON"""
        schema_data = {
            "document_info": {
                "total_pages": len(results.get("pages", [])),
                "ai_enabled": results.get("ai_enabled", False),
                "total_elements": results.get("total_elements", 0),
                "needs_human_review": results.get("human_review_required", False)
            },
            "pages": []
        }
        
        for page in results.get("pages", []):
            page_data = {
                "page_number": page["page_number"],
                "processing_method": page.get("processing_method", "unknown"),
                "elements": page.get("elements", []),
                "relationships": page.get("relationships", []),
                "human_review_tasks": page.get("human_review_tasks", [])
            }
            schema_data["pages"].append(page_data)
        
        return schema_data


# Configuració per defecte d'IA
DEFAULT_AI_CONFIG = {
    "ai_model_path": "src/ai_model/models/best.pt",
    "confidence_threshold": 0.7,
    "human_review_threshold": 0.5,
    "enable_continuous_learning": True,
    "auto_retrain_after_corrections": 50
}


if __name__ == "__main__":
    import pandas as pd
    import logging
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Crear configuració d'exemple
    project_dir = Path(__file__).parent.parent.parent
    config_path = project_dir / "config_ai.json"
    
    if not config_path.exists():
        with open(config_path, 'w') as f:
            json.dump(DEFAULT_AI_CONFIG, f, indent=2)
        print(f"Configuració d'IA creada: {config_path}")
    
    # Inicialitzar pipeline amb IA
    pipeline = AIEnhancedPipeline(str(config_path))
    
    # Mostrar estat
    stats = pipeline.get_model_performance_stats()
    print(f"\nEstat del pipeline d'IA:")
    print(f"- IA disponible: {stats['ai_available']}")
    print(f"- Model carregat: {stats['model_loaded']}")
    print(f"- Total correccions: {stats['total_corrections']}")
    print(f"- Precisió estimada: {stats['accuracy_estimate']:.1%}")
    
    print("\nPipeline d'IA integrat correctament!")
