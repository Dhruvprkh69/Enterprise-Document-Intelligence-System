"""
NLP service for query analysis, intent detection, and text processing.
Enhances RAG with better understanding of user questions.
"""
import re
from typing import Dict, List, Tuple
from enum import Enum


class QuestionType(Enum):
    """Types of questions."""
    WHAT = "what"  # Definition, fact
    WHY = "why"    # Explanation, reasoning
    HOW = "how"    # Process, method
    WHEN = "when"  # Time, date
    WHERE = "where"  # Location
    WHO = "who"    # Person, entity
    WHICH = "which"  # Selection, choice
    UNKNOWN = "unknown"


class IntentType(Enum):
    """User intent types."""
    FACTUAL = "factual"  # Simple fact lookup
    EXPLANATORY = "explanatory"  # Needs explanation
    ANALYTICAL = "analytical"  # Analysis, comparison
    CALCULATIVE = "calculative"  # Calculation needed
    COMPARATIVE = "comparative"  # Comparison
    UNKNOWN = "unknown"


class UserLevel(Enum):
    """User knowledge level."""
    BEGINNER = "beginner"  # Needs simple explanation
    INTERMEDIATE = "intermediate"  # Some knowledge
    EXPERT = "expert"  # Advanced knowledge
    UNKNOWN = "unknown"


class NLPService:
    """NLP service for query analysis and understanding."""
    
    def __init__(self):
        # Question type patterns
        self.question_patterns = {
            QuestionType.WHAT: r'\b(what|what is|what are|what does|what do|what\'s)\b',
            QuestionType.WHY: r'\b(why|why is|why are|why does|why do)\b',
            QuestionType.HOW: r'\b(how|how is|how are|how does|how do|how to|how can)\b',
            QuestionType.WHEN: r'\b(when|when is|when are|when does|when do)\b',
            QuestionType.WHERE: r'\b(where|where is|where are|where does|where do)\b',
            QuestionType.WHO: r'\b(who|who is|who are|who does|who do)\b',
            QuestionType.WHICH: r'\b(which|which is|which are|which does|which do)\b',
        }
        
        # Intent detection keywords
        self.intent_keywords = {
            IntentType.EXPLANATORY: ['explain', 'explanation', 'understand', 'meaning', 'define', 'definition', 
                                     'what is', 'what does', 'tell me about', 'help me understand'],
            IntentType.ANALYTICAL: ['analyze', 'analysis', 'compare', 'comparison', 'relationship', 'correlation',
                                  'impact', 'effect', 'influence', 'trend', 'pattern'],
            IntentType.CALCULATIVE: ['calculate', 'compute', 'ratio', 'percentage', 'margin', 'profit', 'revenue',
                                    'divide', 'multiply', 'sum', 'total', 'average'],
            IntentType.COMPARATIVE: ['compare', 'comparison', 'versus', 'vs', 'difference', 'similar', 'better',
                                    'worse', 'more than', 'less than'],
            IntentType.FACTUAL: ['what', 'who', 'when', 'where', 'which', 'list', 'name', 'show'],
        }
        
        # Confusion indicators
        self.confusion_indicators = [
            'confused', 'confusing', "don't understand", "don't know", "not clear", "unclear",
            "can't understand", "doesn't make sense", "help", "clarify", "simplify"
        ]
        
        # Beginner indicators
        self.beginner_indicators = [
            'what is', 'what does', 'basics', 'simple', 'easy', 'beginner', 'introduction',
            'overview', 'summary', 'in simple terms', 'layman'
        ]
    
    def analyze_question(self, question: str) -> Dict:
        """
        Comprehensive question analysis.
        
        Returns:
            Dict with question_type, intent, user_level, is_confused, needs_explanation
        """
        question_lower = question.lower().strip()
        
        # Detect question type
        question_type = self._detect_question_type(question_lower)
        
        # Detect intent
        intent = self._detect_intent(question_lower)
        
        # Detect user level
        user_level = self._detect_user_level(question_lower)
        
        # Detect confusion
        is_confused = self._detect_confusion(question_lower)
        
        # Needs explanation?
        needs_explanation = (
            intent in [IntentType.EXPLANATORY, IntentType.ANALYTICAL] or
            question_type in [QuestionType.WHAT, QuestionType.WHY, QuestionType.HOW] or
            is_confused or
            user_level == UserLevel.BEGINNER
        )
        
        # Extract key terms/concepts
        key_terms = self._extract_key_terms(question)
        
        return {
            "question_type": question_type.value,
            "intent": intent.value,
            "user_level": user_level.value,
            "is_confused": is_confused,
            "needs_explanation": needs_explanation,
            "key_terms": key_terms,
            "original_question": question
        }
    
    def _detect_question_type(self, question: str) -> QuestionType:
        """Detect what type of question it is."""
        for q_type, pattern in self.question_patterns.items():
            if re.search(pattern, question, re.IGNORECASE):
                return q_type
        return QuestionType.UNKNOWN
    
    def _detect_intent(self, question: str) -> IntentType:
        """Detect user intent from question."""
        # Check each intent type
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in question:
                    return intent
        
        return IntentType.UNKNOWN
    
    def _detect_user_level(self, question: str) -> UserLevel:
        """Detect user's knowledge level."""
        # Check for beginner indicators
        for indicator in self.beginner_indicators:
            if indicator in question:
                return UserLevel.BEGINNER
        
        # Check for expert indicators (complex terms, technical language)
        expert_indicators = ['implementation', 'architecture', 'optimization', 'algorithm', 
                           'methodology', 'framework', 'paradigm']
        for indicator in expert_indicators:
            if indicator in question:
                return UserLevel.EXPERT
        
        return UserLevel.INTERMEDIATE
    
    def _detect_confusion(self, question: str) -> bool:
        """Detect if user is confused."""
        for indicator in self.confusion_indicators:
            if indicator in question:
                return True
        return False
    
    def _extract_key_terms(self, question: str) -> List[str]:
        """Extract key terms/concepts from question."""
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
                     'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
                     'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who',
                     'when', 'where', 'why', 'how', 'and', 'or', 'but', 'if', 'then', 'else'}
        
        # Simple extraction: split and filter
        words = re.findall(r'\b\w+\b', question.lower())
        key_terms = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Remove duplicates, keep order
        seen = set()
        unique_terms = []
        for term in key_terms:
            if term not in seen:
                seen.add(term)
                unique_terms.append(term)
        
        return unique_terms[:5]  # Top 5 terms
    
    def expand_query(self, question: str) -> List[str]:
        """Generate query variations for better retrieval."""
        variations = [question]  # Original question
        
        # Add variations based on question type
        question_lower = question.lower()
        
        # If "what is X", add "X definition", "X meaning", "explain X"
        if 'what is' in question_lower or 'what does' in question_lower:
            # Extract the term after "what is/does"
            match = re.search(r'what (?:is|does) (.+?)(?:\?|$)', question_lower)
            if match:
                term = match.group(1).strip()
                variations.extend([
                    f"{term} definition",
                    f"{term} meaning",
                    f"explain {term}",
                    f"what is {term}"
                ])
        
        # If "how to X", add "X method", "X process", "X steps"
        if 'how to' in question_lower or 'how do' in question_lower:
            match = re.search(r'how (?:to|do) (.+?)(?:\?|$)', question_lower)
            if match:
                term = match.group(1).strip()
                variations.extend([
                    f"{term} method",
                    f"{term} process",
                    f"{term} steps",
                    f"how {term} works"
                ])
        
        return variations[:3]  # Return top 3 variations
