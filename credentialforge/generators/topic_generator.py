"""Topic-specific content generation using LLM."""

import random
from typing import Dict, List, Optional, Any
from ..llm.llama_interface import LlamaInterface
from ..utils.exceptions import GenerationError
from ..utils.language_mapper import LanguageMapper
# Removed PromptSystem - using simplified prompts
from ..utils.language_content_generator import LanguageContentGenerator


class TopicGenerator:
    """Generates topic-specific content using LLM."""
    
    def __init__(self, llm_interface: Optional[LlamaInterface] = None, 
                 language_mapper: Optional[LanguageMapper] = None):
        """Initialize topic generator.
        
        Args:
            llm_interface: Optional LLM interface for content generation
            language_mapper: Optional language mapper for localized content
        """
        self.llm = llm_interface
        self.language_mapper = language_mapper or LanguageMapper()
        self.language_content_generator = LanguageContentGenerator()
        
        # Initialize prompt system for enhanced reasoning
        # Simplified prompt system removed
        
        self.generation_stats = {
            'total_generated': 0,
            'by_topic': {},
            'by_format': {},
            'by_language': {},
            'errors': 0
        }
    
    def generate_topic_content(self, topic: str, file_format: str, 
                              context: Optional[Dict[str, Any]] = None) -> str:
        """Generate topic-specific content for given format.
        
        Args:
            topic: Topic for content generation (can be multiple topics separated by comma)
            file_format: Target file format
            context: Optional context information
            
        Returns:
            Generated content
            
        Raises:
            GenerationError: If content generation fails
        """
        try:
            # Handle multiple topics
            if ',' in topic:
                topics = [t.strip() for t in topic.split(',')]
                content = self._generate_combined_topics(topics, file_format, context)
            else:
                # Generate AI sub-topics for uniqueness
                enhanced_topic = self._generate_ai_subtopics(topic, context)
                
                if self.llm:
                    # Use LLM for content generation with fallback
                    try:
                        content = self._generate_with_llm(enhanced_topic, file_format, context)
                    except Exception as llm_error:
                        content = self._generate_with_template(enhanced_topic, file_format, context)
                else:
                    # Use template-based generation
                    content = self._generate_with_template(enhanced_topic, file_format, context)
            
            # Track generation
            self.generation_stats['total_generated'] += 1
            self.generation_stats['by_topic'][topic] = \
                self.generation_stats['by_topic'].get(topic, 0) + 1
            self.generation_stats['by_format'][file_format] = \
                self.generation_stats['by_format'].get(file_format, 0) + 1
            
            # Track language usage
            if context:
                uniqueness_factors = self._get_uniqueness_factors(context)
                language = uniqueness_factors.get('language', 'en')
                self.generation_stats['by_language'][language] = \
                    self.generation_stats['by_language'].get(language, 0) + 1
            
            return content
            
        except Exception as e:
            self.generation_stats['errors'] += 1
            raise GenerationError(f"Topic content generation failed: {e}")
    
    def generate_multiple_topics(self, topics: List[str], file_format: str,
                                context: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate content for multiple topics.
        
        Args:
            topics: List of topics
            file_format: Target file format
            context: Optional context information
            
        Returns:
            Dictionary mapping topics to generated content
        """
        results = {}
        
        for topic in topics:
            try:
                content = self.generate_topic_content(topic, file_format, context)
                results[topic] = content
            except Exception as e:
                # Log error but continue with other topics
                self.generation_stats['errors'] += 1
                results[topic] = f"Error generating content for {topic}: {e}"
        
        return results
    
    def _generate_combined_topics(self, topics: List[str], file_format: str,
                                 context: Optional[Dict[str, Any]] = None) -> str:
        """Generate content combining multiple topics.
        
        Args:
            topics: List of topics to combine
            file_format: Target file format
            context: Optional context information
            
        Returns:
            Combined content
        """
        # Generate content for each topic
        topic_contents = []
        for topic in topics:
            try:
                if self.llm:
                    try:
                        content = self._generate_with_llm(topic, file_format, context)
                    except Exception:
                        content = self._generate_with_template(topic, file_format, context)
                else:
                    content = self._generate_with_template(topic, file_format, context)
                topic_contents.append(content)
            except Exception:
                # Fallback to simple content for failed topics
                topic_contents.append(f"Content related to {topic}")
        
        # Combine topics into comprehensive document
        combined_content = self._combine_topic_contents(topics, topic_contents, file_format)
        return combined_content
    
    def _combine_topic_contents(self, topics: List[str], contents: List[str], 
                               file_format: str) -> str:
        """Combine multiple topic contents into a comprehensive document.
        
        Args:
            topics: List of topics
            contents: List of content for each topic
            file_format: Target file format
            
        Returns:
            Combined content
        """
        if file_format.lower() in ['eml', 'msg']:
            return self._combine_email_content(topics, contents)
        elif file_format.lower() in ['xlsx', 'xlsm', 'xltm', 'xls', 'xlsb', 'ods']:
            return self._combine_spreadsheet_content(topics, contents)
        elif file_format.lower() in ['pptx', 'ppt', 'odp']:
            return self._combine_presentation_content(topics, contents)
        elif file_format.lower() in ['docx', 'doc', 'docm', 'rtf', 'odf']:
            return self._combine_document_content(topics, contents)
        elif file_format.lower() in ['vsdx', 'vsd', 'vsdm', 'vssx', 'vssm', 'vstx', 'vstm']:
            return self._combine_diagram_content(topics, contents)
        elif file_format.lower() == 'pdf':
            return self._combine_pdf_content(topics, contents)
        else:
            return self._combine_generic_content(topics, contents)
    
    def _combine_email_content(self, topics: List[str], contents: List[str]) -> str:
        """Combine topics into email content."""
        subject = f"Multi-Topic Update: {', '.join(topics[:3])}"
        if len(topics) > 3:
            subject += f" and {len(topics) - 3} more"
        
        body = f"""Subject: {subject}

Dear Team,

I wanted to provide a comprehensive update covering multiple areas of our infrastructure and operations.

"""
        
        for i, (topic, content) in enumerate(zip(topics, contents), 1):
            body += f"""
Section {i}: {topic.title()}
{'=' * (len(topic) + 12)}

{content}

"""
        
        body += """
Please review these updates and let me know if you have any questions or concerns.

Best regards,
System Administrator

---
This is an automated message generated for testing purposes.
"""
        return body
    
    def _generate_ai_subtopics(self, main_topic: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate AI-enhanced topic with sub-topics for uniqueness.
        
        Args:
            main_topic: Main topic to enhance
            context: Optional context information
            
        Returns:
            Enhanced topic with sub-topics
        """
        # Get language from context
        language = context.get('language', 'en') if context else 'en'
        
        # Define sub-topic categories based on main topic
        subtopic_categories = {
            'security audit': [
                'vulnerability assessment', 'penetration testing', 'compliance review',
                'access control analysis', 'data protection audit', 'network security scan',
                'incident response planning', 'security policy review', 'risk assessment'
            ],
            'api testing': [
                'endpoint validation', 'performance testing', 'security testing',
                'load testing', 'integration testing', 'documentation review',
                'authentication testing', 'authorization testing', 'error handling'
            ],
            'database management': [
                'performance optimization', 'backup and recovery', 'security hardening',
                'index optimization', 'query analysis', 'capacity planning',
                'replication setup', 'monitoring configuration', 'maintenance procedures'
            ],
            'cloud migration': [
                'infrastructure assessment', 'application migration', 'data migration',
                'security configuration', 'cost optimization', 'performance tuning',
                'disaster recovery', 'monitoring setup', 'compliance validation'
            ],
            'system monitoring': [
                'performance metrics', 'alert configuration', 'log analysis',
                'capacity planning', 'incident response', 'health checks',
                'reporting setup', 'dashboard configuration', 'automation rules'
            ]
        }
        
        # Get sub-topics for the main topic
        available_subtopics = subtopic_categories.get(main_topic.lower(), [
            'implementation planning', 'configuration management', 'performance optimization',
            'security hardening', 'monitoring setup', 'documentation review',
            'testing procedures', 'maintenance planning', 'troubleshooting guide'
        ])
        
        # Select 2-4 random sub-topics
        import random
        num_subtopics = random.randint(2, min(4, len(available_subtopics)))
        selected_subtopics = random.sample(available_subtopics, num_subtopics)
        
        # Create enhanced topic
        if language == 'en':
            enhanced_topic = f"{main_topic}: {', '.join(selected_subtopics)}"
        else:
            # Localize sub-topics if not English
            localized_subtopics = []
            for subtopic in selected_subtopics:
                localized_subtopic = self.language_content_generator.localize_content(subtopic, language)
                localized_subtopics.append(localized_subtopic)
            
            # Localize main topic
            localized_main_topic = self.language_content_generator.localize_content(main_topic, language)
            enhanced_topic = f"{localized_main_topic}: {', '.join(localized_subtopics)}"
        
        return enhanced_topic
    
    def _localize_complete_content(self, content: str, language: str) -> str:
        """Localize complete content to target language.
        
        Args:
            content: Content to localize
            language: Target language code
            
        Returns:
            Fully localized content
        """
        # First, use the language content generator for basic terms
        localized_content = self.language_content_generator.localize_content(content, language)
        
        # Additional language-specific transformations
        if language == 'fr':
            # French-specific transformations
            localized_content = localized_content.replace('Dear Team,', 'Cher Équipe,')
            localized_content = localized_content.replace('Best regards,', 'Cordialement,')
            localized_content = localized_content.replace('Subject:', 'Objet:')
            localized_content = localized_content.replace('Generated on:', 'Généré le:')
            localized_content = localized_content.replace('System:', 'Système:')
            localized_content = localized_content.replace('Company:', 'Entreprise:')
            localized_content = localized_content.replace('Project:', 'Projet:')
            localized_content = localized_content.replace('Environment:', 'Environnement:')
            localized_content = localized_content.replace('Unique ID:', 'ID Unique:')
            localized_content = localized_content.replace('Language:', 'Langue:')
            localized_content = localized_content.replace('Country:', 'Pays:')
            localized_content = localized_content.replace('Region:', 'Région:')
            
        elif language == 'es':
            # Spanish-specific transformations
            localized_content = localized_content.replace('Dear Team,', 'Estimado Equipo,')
            localized_content = localized_content.replace('Best regards,', 'Saludos cordiales,')
            localized_content = localized_content.replace('Subject:', 'Asunto:')
            localized_content = localized_content.replace('Generated on:', 'Generado el:')
            localized_content = localized_content.replace('System:', 'Sistema:')
            localized_content = localized_content.replace('Company:', 'Empresa:')
            localized_content = localized_content.replace('Project:', 'Proyecto:')
            localized_content = localized_content.replace('Environment:', 'Entorno:')
            localized_content = localized_content.replace('Unique ID:', 'ID Único:')
            localized_content = localized_content.replace('Language:', 'Idioma:')
            localized_content = localized_content.replace('Country:', 'País:')
            localized_content = localized_content.replace('Region:', 'Región:')
            
        elif language == 'de':
            # German-specific transformations
            localized_content = localized_content.replace('Dear Team,', 'Liebes Team,')
            localized_content = localized_content.replace('Best regards,', 'Mit freundlichen Grüßen,')
            localized_content = localized_content.replace('Subject:', 'Betreff:')
            localized_content = localized_content.replace('Generated on:', 'Generiert am:')
            localized_content = localized_content.replace('System:', 'System:')
            localized_content = localized_content.replace('Company:', 'Unternehmen:')
            localized_content = localized_content.replace('Project:', 'Projekt:')
            localized_content = localized_content.replace('Environment:', 'Umgebung:')
            localized_content = localized_content.replace('Unique ID:', 'Eindeutige ID:')
            localized_content = localized_content.replace('Language:', 'Sprache:')
            localized_content = localized_content.replace('Country:', 'Land:')
            localized_content = localized_content.replace('Region:', 'Region:')
        
        return localized_content
    
    def _combine_spreadsheet_content(self, topics: List[str], contents: List[str]) -> str:
        """Combine topics into spreadsheet content."""
        combined = f"""Multi-Topic Configuration Summary
Generated: {self._get_current_date()}

"""
        
        for i, (topic, content) in enumerate(zip(topics, contents), 1):
            combined += f"""
Sheet {i}: {topic.title()}
{'-' * (len(topic) + 10)}

{content}

"""
        
        combined += """
Summary:
- Total topics covered: {len(topics)}
- Configuration sections: {len(topics)}
- Last updated: {self._get_current_date()}
- Status: All configurations validated

Notes:
This spreadsheet contains configuration data for multiple system components.
Each sheet represents a different aspect of the infrastructure.
"""
        return combined
    
    def _combine_presentation_content(self, topics: List[str], contents: List[str]) -> str:
        """Combine topics into presentation content."""
        combined = f"""Multi-Topic System Overview
Comprehensive Infrastructure Documentation

"""
        
        for i, (topic, content) in enumerate(zip(topics, contents), 1):
            combined += f"""
Slide {i}: {topic.title()}
{'-' * (len(topic) + 10)}

{content}

"""
        
        combined += f"""
Summary Slide: Integration Overview
- Total components: {len(topics)}
- Integration points: {len(topics) * 2}
- Dependencies: Cross-component
- Monitoring: Comprehensive coverage

Speaker Notes:
This presentation covers {len(topics)} key areas of our infrastructure.
Each section provides detailed technical information and implementation guidance.
"""
        return combined
    
    def _combine_document_content(self, topics: List[str], contents: List[str]) -> str:
        """Combine topics into document content."""
        combined = f"""COMPREHENSIVE SYSTEM DOCUMENTATION
Multi-Topic Infrastructure Guide

Table of Contents:
"""
        
        for i, topic in enumerate(topics, 1):
            combined += f"{i}. {topic.title()}\n"
        
        combined += f"""
Executive Summary:
This document provides comprehensive coverage of {len(topics)} critical areas of our infrastructure.
Each section contains detailed technical specifications, configuration parameters, and implementation guidelines.

"""
        
        for i, (topic, content) in enumerate(zip(topics, contents), 1):
            combined += f"""
{i}. {topic.upper()}
{'=' * (len(topic) + 4)}

{content}

"""
        
        combined += f"""
Conclusion:
This document serves as a complete reference for {len(topics)} system components.
Regular updates and reviews are recommended to maintain accuracy and relevance.

Document Information:
- Generated: {self._get_current_date()}
- Topics covered: {len(topics)}
- Sections: {len(topics)}
- Status: Current and validated
"""
        return combined
    
    def _combine_diagram_content(self, topics: List[str], contents: List[str]) -> str:
        """Combine topics into diagram content."""
        combined = f"""Multi-Component System Architecture
Comprehensive Infrastructure Diagram

"""
        
        for i, (topic, content) in enumerate(zip(topics, contents), 1):
            combined += f"""
Component {i}: {topic.title()}
{'-' * (len(topic) + 15)}

{content}

"""
        
        combined += f"""
Integration Overview:
- Total components: {len(topics)}
- Data flows: {len(topics) * 2}
- Security boundaries: {len(topics)}
- Monitoring points: {len(topics) * 3}

Legend:
- Solid lines: Direct connections
- Dashed lines: Data flows
- Dotted lines: Security boundaries
- Red boxes: Critical components
- Blue boxes: Supporting services
"""
        return combined
    
    def _combine_pdf_content(self, topics: List[str], contents: List[str]) -> str:
        """Combine topics into PDF content."""
        combined = f"""COMPREHENSIVE SYSTEM DOCUMENTATION
Multi-Topic Infrastructure Reference Guide

Document Overview:
This document provides detailed technical specifications and implementation guidelines for {len(topics)} critical system components.

"""
        
        for i, (topic, content) in enumerate(zip(topics, contents), 1):
            combined += f"""
Chapter {i}: {topic.upper()}
{'=' * (len(topic) + 12)}

{content}

"""
        
        combined += f"""
Document Summary:
- Total chapters: {len(topics)}
- Technical specifications: Complete
- Implementation guidelines: Detailed
- Configuration parameters: Validated
- Security considerations: Addressed

Document Information:
- Version: 1.0
- Generated: {self._get_current_date()}
- Status: Current and approved
- Review cycle: Quarterly
"""
        return combined
    
    def _combine_generic_content(self, topics: List[str], contents: List[str]) -> str:
        """Combine topics into generic content."""
        combined = f"""Multi-Topic Documentation
Comprehensive System Information

"""
        
        for i, (topic, content) in enumerate(zip(topics, contents), 1):
            combined += f"""
Section {i}: {topic.title()}
{'-' * (len(topic) + 12)}

{content}

"""
        
        combined += f"""
Summary:
This document covers {len(topics)} important aspects of our system infrastructure.
Each section provides detailed information and implementation guidance.

Total sections: {len(topics)}
Last updated: {self._get_current_date()}
Status: Current and validated
"""
        return combined
    
    def _generate_with_llm(self, topic: str, file_format: str,
                          context: Optional[Dict[str, Any]] = None) -> str:
        """Generate content using LLM.
        
        Args:
            topic: Topic for content generation
            file_format: Target file format
            context: Optional context information
            
        Returns:
            Generated content
        """
        if not self.llm:
            raise GenerationError("LLM interface not available")
        
        return self.llm.generate_topic_content(topic, file_format, context)
    
    def _generate_with_template(self, topic: str, file_format: str,
                               context: Optional[Dict[str, Any]] = None) -> str:
        """Generate content using templates.
        
        Args:
            topic: Topic for content generation
            file_format: Target file format
            context: Optional context information
            
        Returns:
            Generated content
        """
        # Get language from context
        language = context.get('language', 'en') if context else 'en'
        
        # Get language-specific template
        template = self._get_template(file_format, language)
        
        # Generate content using template
        content = self._fill_template(template, topic, file_format, context)
        
        return content
    
    def _get_template(self, file_format: str, language: str = 'en') -> str:
        """Get template for file format.
        
        Args:
            file_format: Target file format
            language: Target language code
            
        Returns:
            Template string
        """
        templates = {
            'eml': self._get_email_template(language),
            'xlsx': self._get_excel_template(),
            'pptx': self._get_powerpoint_template(),
            'vsdx': self._get_visio_template(),
            'msg': self._get_outlook_template(),
        }
        
        return templates.get(file_format.lower(), self._get_generic_template())
    
    def _get_localized_template(self, file_format: str, language: str = 'en') -> str:
        """Get language-aware template for the specified format."""
        base_template = self._get_template(file_format)
        
        if language == 'en':
            return base_template
        
        # Localize the template content
        localized_template = self.language_content_generator.localize_content(base_template, language)
        return localized_template
    
    def _get_email_template(self, language: str = 'en') -> str:
        """Get language-aware email template."""
        if language == 'fr':
            return """Objet: {topic_title}

Cher Équipe,

J'espère que ce courriel vous trouve en bonne santé. Je voulais vous fournir une mise à jour importante concernant notre implémentation {topic} chez {company} et le statut opérationnel actuel pour {project}.

{content_body}

Statut Actuel:
- {point1}
- {point2}
- {point3}

Détails Techniques:
Notre système {topic} fonctionne parfaitement dans {environment} avec les métriques clés suivantes:
- Temps de fonctionnement: 99,9% au cours des 30 derniers jours
- Temps de réponse: Moyenne 150ms
- Taux d'erreur: Moins de 0,1%
- Débit: 10 000 requêtes par minute
- ID du service: {service_id}
- Projet: {project}

Mises à jour de Configuration:
Les modifications de configuration suivantes ont été implémentées dans le cadre de {timeline}:
- Pool de connexions de base de données optimisé pour {db_host}
- Performance de la couche de cache améliorée
- Protocoles de sécurité mis à jour
- Seuils de surveillance ajustés
- Point de terminaison API: {endpoint}
- Authentification: {auth_type}

Prochaines Étapes:
1. Surveillance et optimisation des performances
2. Audit de sécurité et révision de conformité
3. Mises à jour de documentation et formation
4. Tests de récupération d'urgence

Veuillez examiner la documentation jointe et me faire savoir si vous avez des questions ou des préoccupations.

Cordialement,
{author}

---
Ceci est un message automatisé généré à des fins de test.
Généré le: {date}
Système: Plateforme de Gestion {topic}
Entreprise: {company}
Projet: {project}
Environnement: {environment}
ID Unique: {unique_id}
Version: 2.1.4
"""
        elif language == 'es':
            return """Asunto: {topic_title}

Estimado Equipo,

Espero que este correo electrónico los encuentre bien. Quería proporcionarles una actualización importante sobre nuestra implementación {topic} en {company} y el estado operacional actual para {project}.

{content_body}

Estado Actual:
- {point1}
- {point2}
- {point3}

Detalles Técnicos:
Nuestro sistema {topic} ha estado funcionando sin problemas en {environment} con las siguientes métricas clave:
- Tiempo de actividad: 99,9% en los últimos 30 días
- Tiempo de respuesta: Promedio 150ms
- Tasa de error: Menos del 0,1%
- Rendimiento: 10,000 solicitudes por minuto
- ID del servicio: {service_id}
- Proyecto: {project}

Actualizaciones de Configuración:
Los siguientes cambios de configuración han sido implementados como parte de {timeline}:
- Agrupación de conexiones de base de datos optimizada para {db_host}
- Rendimiento de la capa de caché mejorado
- Protocolos de seguridad actualizados
- Umbrales de monitoreo ajustados
- Punto final de API: {endpoint}
- Autenticación: {auth_type}

Próximos Pasos:
1. Monitoreo y optimización de rendimiento
2. Auditoría de seguridad y revisión de cumplimiento
3. Actualizaciones de documentación y capacitación
4. Pruebas de recuperación ante desastres

Por favor revisen la documentación adjunta y hágamelo saber si tienen alguna pregunta o inquietud.

Saludos cordiales,
{author}

---
Este es un mensaje automatizado generado para propósitos de prueba.
Generado el: {date}
Sistema: Plataforma de Gestión {topic}
Empresa: {company}
Proyecto: {project}
Entorno: {environment}
ID Único: {unique_id}
Versión: 2.1.4
"""
        elif language == 'it':
            return """Oggetto: {topic_title}

Caro Team,

Spero che questa email vi trovi in buona salute. Volevo fornirvi un aggiornamento importante riguardo alla nostra implementazione {topic} presso {company} e lo stato operativo attuale per {project}.

{content_body}

Stato Attuale:
- {point1}
- {point2}
- {point3}

Dettagli Tecnici:
Il nostro sistema {topic} ha funzionato perfettamente in {environment} con le seguenti metriche chiave:
- Tempo di attività: 99,9% negli ultimi 30 giorni
- Tempo di risposta: Media 150ms
- Tasso di errore: Meno dello 0,1%
- Throughput: 10.000 richieste al minuto
- ID del servizio: {service_id}
- Progetto: {project}

Aggiornamenti di Configurazione:
Le seguenti modifiche di configurazione sono state implementate come parte di {timeline}:
- Pool di connessioni database ottimizzato per {db_host}
- Prestazioni del layer di cache migliorate
- Protocolli di sicurezza aggiornati
- Soglie di monitoraggio regolate
- Endpoint API: {endpoint}
- Autenticazione: {auth_type}

Prossimi Passi:
1. Monitoraggio e ottimizzazione delle prestazioni
2. Audit di sicurezza e revisione della conformità
3. Aggiornamenti della documentazione e formazione
4. Test di disaster recovery

Si prega di rivedere la documentazione allegata e farmi sapere se avete domande o preoccupazioni.

Cordiali saluti,
{author}

---
Questo è un messaggio automatizzato generato per scopi di test.
Generato il: {date}
Sistema: Piattaforma di Gestione {topic}
Azienda: {company}
Progetto: {project}
Ambiente: {environment}
ID Unico: {unique_id}
Versione: 2.1.4
"""
        elif language == 'de':
            return """Betreff: {topic_title}

Liebes Team,

Ich hoffe, diese E-Mail erreicht Sie in guter Verfassung. Ich wollte Ihnen ein wichtiges Update bezüglich unserer {topic} Implementierung bei {company} und dem aktuellen operativen Status für {project} geben.

{content_body}

Aktueller Status:
- {point1}
- {point2}
- {point3}

Technische Details:
Unser {topic} System läuft reibungslos in {environment} mit den folgenden Schlüsselmetriken:
- Betriebszeit: 99,9% in den letzten 30 Tagen
- Antwortzeit: Durchschnitt 150ms
- Fehlerrate: Weniger als 0,1%
- Durchsatz: 10.000 Anfragen pro Minute
- Service-ID: {service_id}
- Projekt: {project}

Konfigurations-Updates:
Die folgenden Konfigurationsänderungen wurden als Teil von {timeline} implementiert:
- Datenbankverbindungspooling optimiert für {db_host}
- Cache-Layer-Leistung verbessert
- Sicherheitsprotokolle aktualisiert
- Überwachungsschwellen angepasst
- API-Endpunkt: {endpoint}
- Authentifizierung: {auth_type}

Nächste Schritte:
1. Leistungsüberwachung und -optimierung
2. Sicherheitsaudit und Compliance-Überprüfung
3. Dokumentations-Updates und Schulung
4. Disaster-Recovery-Tests

Bitte überprüfen Sie die beigefügte Dokumentation und lassen Sie mich wissen, wenn Sie Fragen oder Bedenken haben.

Mit freundlichen Grüßen,
{author}

---
Dies ist eine automatisierte Nachricht, die zu Testzwecken generiert wurde.
Generiert am: {date}
System: {topic} Management Platform
Unternehmen: {company}
Projekt: {project}
Umgebung: {environment}
Eindeutige ID: {unique_id}
Version: 2.1.4
"""
        else:  # English
            return """Subject: {topic_title}

Dear Team,

I hope this email finds you well. I wanted to provide you with an important update regarding our {topic} implementation at {company} and current operational status for {project}.

{content_body}

Current Status:
- {point1}
- {point2}
- {point3}

Technical Details:
Our {topic} system has been running smoothly in {environment} with the following key metrics:
- Uptime: 99.9% over the last 30 days
- Response time: Average 150ms
- Error rate: Less than 0.1%
- Throughput: 10,000 requests per minute
- Service ID: {service_id}
- Project: {project}

Configuration Updates:
The following configuration changes have been implemented as part of {timeline}:
- Database connection pooling optimized for {db_host}
- Cache layer performance improved
- Security protocols updated
- Monitoring thresholds adjusted
- API endpoint: {endpoint}
- Authentication: {auth_type}

Next Steps:
1. Performance monitoring and optimization
2. Security audit and compliance review
3. Documentation updates and training
4. Disaster recovery testing

Please review the attached documentation and let me know if you have any questions or concerns.

Best regards,
{author}

---
This is an automated message generated for testing purposes.
Generated on: {date}
System: {topic} Management Platform
Company: {company}
Project: {project}
Environment: {environment}
Unique ID: {unique_id}
Version: 2.1.4
"""
    
    def _get_excel_template(self) -> str:
        """Get Excel template."""
        return """{topic_title} - Comprehensive Configuration Data

EXECUTIVE SUMMARY:
This spreadsheet contains detailed configuration parameters for our {topic} infrastructure at {company}.
All settings have been validated and are currently in production use as part of {project}.

SERVICE CONFIGURATION:
Service Name: {service_name}
Service ID: {service_id}
Primary Endpoint: {endpoint}
Secondary Endpoint: {backup_endpoint}
Status: Active and Monitored
Last Updated: {date}
Next Review: {next_review_date}
Service Owner: {author}
Criticality Level: High
Project: {project}
Environment: {environment}
Timeline: {timeline}

DATABASE CONFIGURATION:
Primary Host: {db_host}
Secondary Host: {db_backup_host}
Port: {db_port}
Database: {db_name}
Connection Pool: {pool_size}
Max Connections: 100
Timeout: 30 seconds
SSL: Enabled
Backup Schedule: Daily at 2:00 AM
Retention: 30 days

API CONFIGURATION:
Base URL: {api_url}
Version: {api_version}
Authentication: {auth_type}
Rate Limit: {rate_limit}
Timeout: 30 seconds
Retry Policy: 3 attempts with exponential backoff
Circuit Breaker: Enabled
Load Balancing: Round Robin

SECURITY CONFIGURATION:
Encryption: AES-256
Key Rotation: Every 90 days
Access Control: Role-based
Audit Logging: Enabled
Compliance: SOC 2 Type II
Penetration Testing: Quarterly

MONITORING & ALERTING:
Health Check: {health_endpoint}
Metrics: {metrics_endpoint}
Logs: {logs_endpoint}
Dashboard: https://monitoring.{domain}/{topic}
Alert Channels: Email, Slack, PagerDuty
SLA: 99.9% uptime
Response Time: < 200ms

PERFORMANCE METRICS:
Average Response Time: 150ms
Peak Throughput: 10,000 req/min
Error Rate: < 0.1%
CPU Usage: 45%
Memory Usage: 2.1GB
Disk Usage: 15GB

DEPLOYMENT INFORMATION:
Environment: {environment}
Deployment Method: Blue-Green
Rollback Strategy: Automated
Testing: Automated CI/CD
Compliance: PCI DSS Level 1

CONFIGURATION PARAMETERS:
{config1}
{config2}
{config3}
{config4}
{config5}

NOTES & MAINTENANCE:
{notes}

Maintenance Window: Sunday 2:00-4:00 AM EST
Contact: devops@{domain}
Emergency Contact: +1-555-0123
Documentation: https://docs.{domain}/{topic}
Unique ID: {unique_id}
"""
    
    def _get_powerpoint_template(self) -> str:
        """Get PowerPoint template."""
        return """{topic_title}

Slide 1: Overview
- {topic} implementation
- Key components and architecture
- Integration points

Slide 2: Technical Details
- System requirements
- Configuration parameters
- Performance metrics

Slide 3: Implementation
- Deployment steps
- Configuration files
- Environment variables

Slide 4: Monitoring
- Health checks
- Metrics collection
- Alerting rules

Slide 5: Security
- Authentication methods
- Access controls
- Audit logging

Speaker Notes:
{notes}
"""
    
    def _get_visio_template(self) -> str:
        """Get Visio template."""
        return """{topic_title} - System Architecture

Components:
- {component1}: {description1}
- {component2}: {description2}
- {component3}: {description3}

Connections:
- {connection1}
- {connection2}
- {connection3}

Data Flow:
- {flow1}
- {flow2}
- {flow3}

Configuration:
- {config1}
- {config2}
- {config3}

Notes:
{notes}
"""
    
    def _get_outlook_template(self) -> str:
        """Get Outlook message template."""
        return """{topic_title}

Hi Team,

I wanted to provide an update on our {topic} implementation.

Current Status:
- {status1}
- {status2}
- {status3}

Next Steps:
- {step1}
- {step2}
- {step3}

Please review and let me know your thoughts.

Thanks,
{author}

---
Generated for testing purposes.
"""
    
    def _get_generic_template(self) -> str:
        """Get generic template."""
        return """{topic_title}

Overview:
{topic} implementation details and configuration.

Key Components:
- {component1}
- {component2}
- {component3}

Configuration:
- {config1}
- {config2}
- {config3}

Notes:
{notes}
"""
    
    def _fill_template(self, template: str, topic: str, file_format: str,
                      context: Optional[Dict[str, Any]] = None) -> str:
        """Fill template with generated content.
        
        Args:
            template: Template string
            topic: Topic for content generation
            file_format: Target file format
            context: Optional context information
            
        Returns:
            Filled template
        """
        # Generate template variables
        variables = self._generate_template_variables(topic, file_format, context)
        
        # Fill template
        try:
            content = template.format(**variables)
        except KeyError as e:
            # Handle missing template variables by providing defaults
            default_variables = {
                'topic_title': f"{topic.title()} Documentation",
                'topic': topic,
                'content_body': f"Content related to {topic}",
                'point1': f"Implementation of {topic} requires careful planning",
                'point2': f"Configuration management for {topic} is critical", 
                'point3': f"Monitoring and alerting for {topic} should be established",
                'author': 'System Admin',
                'date': self._get_current_date(),
                'notes': f"Additional notes and considerations for {topic} implementation."
            }
            # Merge with existing variables
            all_variables = {**default_variables, **variables}
            content = template.format(**all_variables)
        
        return content
    
    def _generate_template_variables(self, topic: str, file_format: str,
                                   context: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate unique variables for template filling.
        
        Args:
            topic: Topic for content generation
            file_format: Target file format
            context: Optional context information
            
        Returns:
            Dictionary of template variables
        """
        # Get uniqueness factors for content variation
        uniqueness_factors = self._get_uniqueness_factors(context)
        
        # Generate unique content variations
        file_index = context.get('file_index', 0) if context else 0
        
        # Unique company and project details
        company = uniqueness_factors['company']
        project = uniqueness_factors['project']
        environment = uniqueness_factors['environment']
        timeline = uniqueness_factors['timeline']
        language = uniqueness_factors['language']
        country = uniqueness_factors['country']
        region = uniqueness_factors['region']
        
        # Generate unique technical details
        unique_id = f"{file_index:04d}"
        service_id = f"svc-{unique_id}"
        api_version = f"v{random.randint(1, 3)}.{random.randint(0, 9)}"
        port = random.randint(8000, 9999)
        pool_size = random.randint(5, 50)
        rate_limit = f"{random.randint(100, 10000)}/hour"
        
        # Unique endpoints and configurations
        domain = f"{company.lower().replace(' ', '').replace('corp', '').replace('inc', '').replace('ltd', '')}.com"
        service_name = f"{topic.replace(' ', '_').lower()}_{service_id}"
        
        variables = {
            'topic_title': f"{topic.title()} - {project} Implementation",
            'topic': topic,
            'author': random.choice([
                f'John Smith - {company}', f'Sarah Johnson - {company}', 
                f'Mike Chen - {company}', f'Lisa Rodriguez - {company}',
                f'David Kim - {company}', f'Emma Wilson - {company}'
            ]),
            'date': self._get_current_date(),
            'next_review_date': self._get_future_date(),
            'company': company,
            'project': project,
            'environment': environment,
            'timeline': timeline,
            'service_name': service_name,
            'service_id': service_id,
            'endpoint': f"https://api.{domain}/{topic.replace(' ', '/').lower()}",
            'backup_endpoint': f"https://backup-api.{domain}/{topic.replace(' ', '/').lower()}",
            'point1': f"Implementation of {topic} for {project} requires careful planning and coordination",
            'point2': f"Configuration management for {topic} in {environment} is critical for success",
            'point3': f"Monitoring and alerting for {topic} should be established as part of {timeline}",
            'component1': f"{topic} Core Component - {service_id}",
            'component2': f"{topic} Integration Layer - {project}",
            'component3': f"{topic} Monitoring Service - {company}",
            'description1': f"Main component handling {topic} operations for {project}",
            'description2': f"Integration layer for {topic} connectivity in {environment}",
            'description3': f"Monitoring service for {topic} health and performance",
            'connection1': f"{topic} to {company} Database Cluster",
            'connection2': f"{topic} to {project} API Gateway",
            'connection3': f"{topic} to {company} Monitoring System",
            'flow1': f"Data flow in {topic} processing for {project}",
            'flow2': f"Authentication flow for {topic} in {environment}",
            'flow3': f"Error handling flow in {topic} system",
            'config1': f"{topic.upper()}_HOST={service_name}.{domain}",
            'config2': f"{topic.upper()}_PORT={port}",
            'config3': f"{topic.upper()}_DEBUG=false",
            'config4': f"{topic.upper()}_ENVIRONMENT={environment}",
            'config5': f"{topic.upper()}_PROJECT={project}",
            'db_host': f"db-{unique_id}.{domain}",
            'db_backup_host': f"db-backup-{unique_id}.{domain}",
            'db_port': str(port + 1000),
            'db_name': f"{topic.replace(' ', '_').lower()}_{project.lower().replace(' ', '_')}_db",
            'pool_size': str(pool_size),
            'api_url': f"https://api.{domain}/{topic.replace(' ', '/').lower()}",
            'api_version': api_version,
            'auth_type': random.choice(['JWT', 'OAuth2', 'API Key', 'Bearer Token']),
            'rate_limit': rate_limit,
            'health_endpoint': f"/health/{topic.replace(' ', '/').lower()}/{service_id}",
            'metrics_endpoint': f"/metrics/{topic.replace(' ', '/').lower()}/{project}",
            'logs_endpoint': f"/logs/{topic.replace(' ', '/').lower()}/{company}",
            'status1': f"{topic} service is running in {environment}",
            'status2': f"{topic} configuration is valid for {project}",
            'status3': f"{topic} monitoring is active and reporting to {company}",
            'step1': f"Review {topic} configuration for {project}",
            'step2': f"Test {topic} functionality in {environment}",
            'step3': f"Deploy {topic} to production as part of {timeline}",
            'notes': f"Additional notes and considerations for {topic} implementation in {project} by {company}.",
            'unique_id': unique_id,
            'domain': domain,
            'language': language,
            'country': country,
            'region': region
        }
        
        # Add context variables if provided
        if context:
            variables.update(context)
        
        return variables
    
    def _get_uniqueness_factors(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate uniqueness factors to ensure content variation.
        
        Args:
            context: Optional context information
            
        Returns:
            Dictionary of uniqueness factors
        """
        import time
        
        # Company variations - include both generic and AXA companies
        companies = [
            # Generic companies (English)
            "TechCorp Solutions", "DataFlow Systems", "CloudScale Technologies", 
            "SecureNet Enterprises", "InnovateLab Inc", "DigitalBridge Corp",
            "NextGen Systems", "CyberShield Technologies", "QuantumSoft Solutions",
            "EliteTech Industries", "ProActive Systems", "FutureTech Dynamics",
            
            # AXA companies (multi-language)
            "AXA France IARD", "AXA France Vie", "AXA Partners",
            "AXA Assicurazioni SpA", "AXA Banca Monte dei Paschi di Siena S.p.A.",
            "AXA Seguros Generales, S.A. de Seguros y Reaseguros", "AXA Mediterranean Holding, S.A.U.",
            "AXA Konzern AG", "AXA Versicherung AG", "AXA Krankenversicherung AG",
            "AXA China", "AXA Brasil Servicios de Consultoria de Negocios Ltda",
            "AXA Colpatria Seguros S.A.", "AXA UK PLC", "AXA Insurance PLC",
            "AXA Luxembourg SA", "AXA Belgium", "AXA Ireland Limited"
        ]
        
        # Project variations
        projects = [
            "Project Phoenix", "Operation Thunder", "System Alpha", "Initiative Beta",
            "Mission Control", "Project Genesis", "Operation Storm", "System Nova",
            "Initiative Titan", "Mission Vector", "Project Quantum", "Operation Matrix"
        ]
        
        # Environment variations
        environments = [
            "Production AWS Cloud", "Development Azure Environment", "Staging GCP Platform",
            "Hybrid Cloud Infrastructure", "On-Premises Data Center", "Multi-Cloud Setup",
            "Containerized Kubernetes", "Serverless Architecture", "Microservices Platform",
            "Edge Computing Network", "Distributed Systems", "High-Availability Cluster"
        ]
        
        # Timeline variations
        timelines = [
            "Q1 2024 Implementation", "Q2 2024 Deployment", "Q3 2024 Migration",
            "Q4 2024 Rollout", "January 2024 Launch", "February 2024 Go-Live",
            "March 2024 Release", "April 2024 Update", "May 2024 Enhancement",
            "June 2024 Upgrade", "July 2024 Modernization", "August 2024 Optimization"
        ]
        
        # Use context file_index for additional variation if available
        file_index = context.get('file_index', 0) if context else 0
        random.seed(file_index + int(time.time() * 1000) % 10000)
        
        # Select company and get its language
        # Check if specific language is requested in context
        requested_language = context.get('language') if context else None
        
        if requested_language and requested_language != 'all' and requested_language != 'en':
            # Filter companies by requested language
            companies_in_language = self.language_mapper.get_companies_by_language(requested_language)
            if companies_in_language:
                companies = companies_in_language
                self.logger.info(f"Filtered companies for language {requested_language}: {len(companies)} companies found")
        
        selected_company = random.choice(companies)
        company_info = self.language_mapper.get_company_info(selected_company)
        
        # Use requested language if specified, otherwise use company language
        final_language = requested_language if requested_language and requested_language != 'all' else company_info.get('language', 'en')
        
        return {
            'company': selected_company,
            'project': random.choice(projects),
            'environment': random.choice(environments),
            'timeline': random.choice(timelines),
            'language': final_language,
            'country': company_info.get('country', 'United States'),
            'region': company_info.get('region', 'North America')
        }
    
    def _get_future_date(self) -> str:
        """Get a future date string.
        
        Returns:
            Future date in YYYY-MM-DD format
        """
        from datetime import datetime, timedelta
        future_date = datetime.now() + timedelta(days=random.randint(30, 365))
        return future_date.strftime('%Y-%m-%d')
    
    def _get_current_date(self) -> str:
        """Get current date string.
        
        Returns:
            Current date in YYYY-MM-DD format
        """
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d')
    
    def get_suggested_topics(self, file_format: str) -> List[str]:
        """Get suggested topics for file format.
        
        Args:
            file_format: Target file format
            
        Returns:
            List of suggested topics
        """
        topic_suggestions = {
            'eml': [
                'system maintenance notification',
                'security update announcement',
                'configuration change notice',
                'deployment status update',
                'incident response report'
            ],
            'xlsx': [
                'API configuration spreadsheet',
                'database connection settings',
                'service endpoint documentation',
                'monitoring metrics data',
                'security audit results'
            ],
            'pptx': [
                'system architecture overview',
                'security implementation guide',
                'deployment procedures',
                'monitoring and alerting setup',
                'compliance documentation'
            ],
            'vsdx': [
                'network topology diagram',
                'system architecture flow',
                'database schema design',
                'API integration map',
                'security control matrix'
            ]
        }
        
        return topic_suggestions.get(file_format.lower(), [
            'system documentation',
            'configuration management',
            'security implementation',
            'monitoring setup',
            'deployment procedures'
        ])
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics.
        
        Returns:
            Dictionary with generation statistics
        """
        return {
            'total_generated': self.generation_stats['total_generated'],
            'by_topic': self.generation_stats['by_topic'].copy(),
            'by_format': self.generation_stats['by_format'].copy(),
            'by_language': self.generation_stats['by_language'].copy(),
            'errors': self.generation_stats['errors'],
            'topics': list(self.generation_stats['by_topic'].keys()),
            'formats': list(self.generation_stats['by_format'].keys()),
            'languages': list(self.generation_stats['by_language'].keys())
        }
    
    def clear_stats(self) -> None:
        """Clear generation statistics."""
        self.generation_stats = {
            'total_generated': 0,
            'by_topic': {},
            'by_format': {},
            'by_language': {},
            'errors': 0
        }
