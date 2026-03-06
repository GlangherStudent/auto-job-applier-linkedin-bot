"""
JobMatcher v2.1 - integration helper for runAiBot.py.
Features: robust paths, optional imports, personal configuration (PERSONALS + QUESTIONS_PERSONAL).
"""

import json
from config.constants import SalaryConversion, TimeConversion, CSVConstants, NetworkConstants, AntiDetectionConstants, RetryConstants, DateConstants, LinkedInURLs
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Optional imports with graceful fallback
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    TFIDF_AVAILABLE = True
except ImportError:
    TFIDF_AVAILABLE = False
    TfidfVectorizer = None
    cosine_similarity = None
    try:
        print("⚠️ sklearn not installed - TF-IDF disabled in JobMatcher")
    except Exception:
        pass

try:
    from fuzzywuzzy import fuzz, process
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False
    fuzz = None
    process = None
    try:
        print("⚠️ fuzzywuzzy not installed - fuzzy matching disabled in JobMatcher")
    except Exception:
        pass


def _build_personals_fallback() -> Dict:
    """Fallback when PERSONALS / QUESTIONS_PERSONAL are not available."""
    try:
        from config.personals import (
            first_name, last_name, middle_name, phone_number,
            current_city, street, state, zipcode, country
        )
        from config.questions import desired_salary, years_of_experience, education
        _fn = (f"{first_name} " + (f"{middle_name} " if middle_name else "") + last_name).replace("  ", " ").strip()
        return {
            "desired_salary": str(int(desired_salary)),
            "city": current_city or "Bucharest, Romania",
            "phone": phone_number,
            "first_name": first_name,
            "last_name": last_name,
            "full_name": _fn,
            "years_of_experience": str(years_of_experience) if years_of_experience else "5",
            "education": education.strip() if isinstance(education, str) else str(education),
            "street": street,
            "state": state,
            "zipcode": zipcode,
            "country": country or "Romania",
        }
    except Exception:
        return {
            "desired_salary": "15000",
            "city": "Bucharest, Romania",
            "phone": "",
            "first_name": "",
            "last_name": "",
            "full_name": "",
            "years_of_experience": "5",
            "education": "Bachelor's degree or equivalent",
            "street": "",
            "state": "",
            "zipcode": "",
            "country": "Romania",
        }


def _load_personals() -> Dict:
    """Merge PERSONALS from config.personals with QUESTIONS_PERSONAL from config.questions."""
    try:
        from config.personals import PERSONALS
        from config.questions import QUESTIONS_PERSONAL
        out = dict(PERSONALS)
        out.update(QUESTIONS_PERSONAL)
        return out
    except ImportError:
        return _build_personals_fallback()


class JobMatcher:
    def __init__(self, db_path: Optional[str] = None):
        """Robust path resolution for config/keywords_db.json."""
        if db_path is None:
            db_path = Path(__file__).resolve().parent.parent / "config" / "keywords_db.json"
        else:
            db_path = Path(db_path)

        if not db_path.exists():
            raise FileNotFoundError(f"keywords_db.json not found: {db_path}")

        with open(db_path, "r", encoding="utf-8") as f:
            self.db = json.load(f)

        self.categories = self.db["categories"]
        self.personals = _load_personals()
        self._init_matchers()

    def _safe_get_data_field(self, data: Dict, field: str, default=None):
        """Safe accessor for missing fields (for example, missing exact_matches/fuzzy_keywords)."""
        return data.get(field, default)

    def _init_matchers(self):
        """Initialise TF-IDF and fuzzy matchers only when the libraries are available."""
        self.tfidf_categories = []
        self.tfidf_vec = None
        self.tfidf_matrix = None
        all_patterns = []

        for cat, data in self.categories.items():
            exact = self._safe_get_data_field(data, "exact_matches", [])
            fuzzy_kws = self._safe_get_data_field(data, "fuzzy_keywords", [])
            patterns = exact + fuzzy_kws
            if patterns:
                all_patterns.extend(patterns)
                self.tfidf_categories.extend([cat] * len(patterns))

        if TFIDF_AVAILABLE and all_patterns and TfidfVectorizer is not None:
            self.tfidf_vec = TfidfVectorizer(ngram_range=(1, 3), stop_words="english", lowercase=True, min_df=1)
            self.tfidf_matrix = self.tfidf_vec.fit_transform(all_patterns)

        self.fuzzy_patterns = {}
        for cat, data in self.categories.items():
            exact = self._safe_get_data_field(data, "exact_matches", [])
            for pattern in exact:
                self.fuzzy_patterns[pattern] = cat

    def preprocess(self, text: str) -> str:
        """Normalize text."""
        text = re.sub(r"[^\w\s]", " ", text.lower().strip())
        return re.sub(r"\s+", " ", text).strip()

    def match_exact(self, question: str) -> Tuple[Optional[str], float]:
        """Layer 1: Exact + fuzzy_keywords."""
        q_clean = self.preprocess(question)
        for cat, data in self.categories.items():
            exact = self._safe_get_data_field(data, "exact_matches", [])
            fuzzy_kws = self._safe_get_data_field(data, "fuzzy_keywords", [])
            for kw in exact:
                if kw.lower() in q_clean:
                    return cat, 1.0
            for kw in fuzzy_kws:
                if kw.lower() in q_clean:
                    return cat, 0.92
        return None, 0.0

    def match_tfidf(self, question: str, min_score: float = 0.65) -> Tuple[Optional[str], float]:
        """Layer 2: TF-IDF, only if the dependency is available."""
        if not TFIDF_AVAILABLE or not self.tfidf_vec or self.tfidf_matrix is None or cosine_similarity is None:
            return None, 0.0
        q_vec = self.tfidf_vec.transform([self.preprocess(question)])
        scores = cosine_similarity(q_vec, self.tfidf_matrix)[0]
        best_idx = scores.argmax()
        sc = float(scores[best_idx])
        if sc >= min_score:
            return self.tfidf_categories[best_idx], sc
        return None, 0.0

    def match_fuzzy(self, question: str, min_score: int = 72) -> Tuple[Optional[str], float]:
        """Layer 3: fuzzy matching, only if the dependency is available."""
        if not FUZZY_AVAILABLE or not self.fuzzy_patterns or process is None:
            return None, 0.0
        try:
            best = process.extractOne(
                self.preprocess(question),
                list(self.fuzzy_patterns.keys()),
                scorer=fuzz.token_set_ratio,
                score_cutoff=min_score,
            )
        except Exception:
            return None, 0.0
        if best:
            return self.fuzzy_patterns[best[0]], best[1] / 100.0
        return None, 0.0

    def _format_response(self, category: str) -> str:
        """Format a response using personal data and a template with {key} placeholders."""
        data = self.categories.get(category, {})
        template = data.get("response_template", "")
        if not template:
            return ""
        if data.get("use_personal_data") and data.get("personal_key"):
            key = data["personal_key"]
            val = self.personals.get(key, "")
            try:
                return template.format(**{key: val})
            except KeyError:
                return str(val) if val else template
        return template

    def match(self, question: str) -> Dict:
        """Full matching pipeline: exact -> TF-IDF -> fuzzy -> unknown."""
        cat, conf = self.match_exact(question)
        if cat and conf >= 0.85:
            return {
                "category": cat, "confidence": conf, "method": "exact",
                "response": self._format_response(cat), "field_type": "text",
            }
        cat, conf = self.match_tfidf(question)
        if cat and conf >= 0.70:
            return {
                "category": cat, "confidence": conf, "method": "tfidf",
                "response": self._format_response(cat), "field_type": "text",
            }
        cat, conf = self.match_fuzzy(question)
        if cat and conf >= 0.72:
            return {
                "category": cat, "confidence": conf, "method": "fuzzy",
                "response": self._format_response(cat), "field_type": "text",
            }
        return {
            "category": "unknown", "confidence": 0.0, "method": "fallback",
            "response": self.categories.get("unknown", {}).get("response_template", "Please discuss in interview."),
            "field_type": "text",
        }


def smart_text_answer(question: str, matcher: Optional[JobMatcher]) -> Optional[str]:
    """For TEXT fields, return an answer when confidence >= 0.70, otherwise None."""
    if matcher is None:
        return None
    result = matcher.match(question)
    if result["confidence"] >= 0.70 and result.get("response"):
        return result["response"]
    return None


# Singleton used by runAiBot (if initialisation succeeds)
job_matcher: Optional[JobMatcher] = None
try:
    job_matcher = JobMatcher()
except Exception as e:
    job_matcher = None
    if "keywords_db" not in str(e).lower():
        print(f"⚠️ JobMatcher not available: {e}")


if __name__ == "__main__":
    from modules.job_matcher import JobMatcher, smart_text_answer, job_matcher
    tests = [
        "What are your salary expectations?",
        "Where do you live?",
        "Desired salary?",
        "What is your first name?",
        "Are you eligible to work?",
    ]
    print("=== JobMatcher Test ===\n")
    for q in tests:
        ans = smart_text_answer(q, job_matcher)
        print(f"Q: {q}")
        print(f"A: {ans or 'None (fallback)'}\n")
