import json
import logging
from PyQt6.QtWebEngineCore import QWebEnginePage

logger = logging.getLogger("GhostBrowser.Injector")

def get_smart_injection_js(field_type, value):
    """
    Concept Breakdown: Heuristic Mapping
    This function generates JS that 'hunts' for the right box to fill.
    It doesn't just look for an ID; it looks for clues in the HTML.
    """
    # Common clues found in HTML for different types of data
    clues = {
        "full_name": ["name", "fullname", "cardholder", "billing-name"],
        "email": ["email", "login", "user", "identifier"],
        "phone": ["phone", "tel", "mobile"],
        "street": ["address", "street", "line1"],
        "city": ["city"],
        "state": ["state", "province"],
        "zip": ["zip", "postal"],
        "cc_num": ["cardnumber", "cc-num", "creditcard"]
    }
    
    target_clues = json.dumps(clues.get(field_type, []))
    safe_value = json.dumps(value)

    # This is the actual JavaScript that runs INSIDE the webpage
    return f"""
    (function() {{
        const targetClues = {target_clues};
        const val = {safe_value};
        const inputs = document.querySelectorAll('input, select, textarea');
        
        inputs.forEach(el => {{
            // We check ID, Name, Placeholder, and Autocomplete for our 'clues'
            const attributes = [el.id, el.name, el.placeholder, el.getAttribute('autocomplete')];
            const match = attributes.some(attr => 
                attr && targetClues.some(clue => attr.toLowerCase().includes(clue.toLowerCase()))
            );

            if (match) {{
                el.value = val;
                // Dispatch events so React/Vue/Angular sites 'see' the change
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                el.style.border = "2px solid #ff6600"; // Visual indicator it worked!
            }}
        }});
    }})();
    """