"""
Identifier Normalizer
Cleans and standardizes messy technical alphanumeric identifiers.
"""
import re

class IdentifierNormalizer:
    @staticmethod
    def normalize_token(token: str) -> str:
        """
        Strips whitespace, hyphens, periods, underscores, and case differences.
        Example: 'P.S.04-A' -> 'PS04A'
                 'PS-04'    -> 'PS04'
                 'IV-21'    -> 'IV21'
                 'HP unit'  -> 'HPU'
        """
        if not token:
            return ""
        s = token.strip().upper()
        
        # Specific domain phrase mapping
        if s in ["HP UNIT", "HYDRAULIC UNIT", "HYDRAULIC POWER PACK", "THE UNIT", "HYDRAULIC PACK"]:
            return "HPU"
        if s in ["ISOLATION VALVE", "ISOLATION VALVE 21", "IV21", "IV-21"]:
            return "IV21"
        if s in ["AEGIS CONTROLLER", "CONTROLLER", "HCS CONTROLLER", "PLC03", "PLC-03"]:
            return "PLC03"
        if s in ["PRESSURE XDCR", "PRESSURE TRANSDUCER", "HPU DISCHARGE PRESSURE TRANSDUCER"]:
            return "PRESSURE_XDCR"

        # General alphanumeric clean
        cleaned = re.sub(r"[\.\-\s_]", "", s)
        return cleaned

    @staticmethod
    def to_canonical_id(raw_id: str) -> str:
        """
        Converts normalized tokens to canonical dash-separated IDs.
        e.g., 'PS04A' -> 'PS-04A'
              'PS04'  -> 'PS-04'
              'PS40'  -> 'PS-40'
              'IV21'  -> 'IV-21'
              'PLC03' -> 'PLC-03'
        """
        norm = IdentifierNormalizer.normalize_token(raw_id)
        
        # Regex match for standard patterns (handles PS04, P04, PS04A, P04A, PS40, P40)
        m_ps = re.match(r"^P(?:S)?0?([0-9]+)([A-Z]?)$", norm)
        if m_ps:
            num = int(m_ps.group(1))
            suffix = m_ps.group(2)
            if num == 4:
                return f"PS-04{suffix}"
            elif num == 40:
                return "PS-40"
            else:
                return f"PS-{num:02d}{suffix}"

        m_iv = re.match(r"^IV0?([0-9]+)$", norm)
        if m_iv:
            return f"IV-{int(m_iv.group(1)):02d}"

        m_plc = re.match(r"^PLC0?([0-9]+)$", norm)
        if m_plc:
            return f"PLC-{int(m_plc.group(1)):02d}"

        if norm in ["HPU", "PRESSURE_XDCR"]:
            return norm

        return raw_id.strip()

