import openai

class PreApprovalEngine:
    """
    AI-Powered Pre-Approval Engine using OpenAI GPT.
    Returns "approve" or "disapprove" based on user and Plaid financial data.
    """

    def __init__(self, openai_api_key: str, model: str = "gpt-4"):
        self.api_key = openai_api_key
        self.model = model
        openai.api_key = self.api_key

    def _safe_float(self, value):
        """Convert numbers like '$455,000' into float."""
        try:
            return float(str(value).replace("$", "").replace(",", "").strip())
        except:
            return 0.0

    def analyze(self, user_input: dict, plaid_data: dict) -> str:
        """
        Returns 'approve' or 'disapprove'.
        """

        # Extract numbers safely
        annual_income = self._safe_float(plaid_data["loan_application"].get("annual_income"))
        purchase_price = self._safe_float(plaid_data["loan_application"].get("purchase_price"))
        down_payment = self._safe_float(plaid_data["loan_application"].get("down_payment"))
        liquid_assets = self._safe_float(plaid_data.get("total_balance", "0"))

        # Derived metrics
        monthly_income = annual_income / 12 if annual_income > 0 else 0
        down_payment_percentage = (down_payment / purchase_price * 100) if purchase_price > 0 else 0


        # Build prompt with correct fields
        prompt = f"""
You are a professional mortgage advisor.
Given the following user financial information, decide if the mortgage should be approved or disapproved.
Return ONLY one word: "approve" or "disapprove".

Approval criteria:
- Debt-to-Income ratio <= 50%
- Down Payment >= 3% of purchase price
- Liquid Assets sufficient to cover at least 1 month of estimated mortgage
  (assume mortgage = 0.5% of purchase price monthly)

User Input:
Full Name: {user_input.get('full_name')}
Email: {user_input.get('email')}
Phone Number: {user_input.get('phone')}
Property Zip Code: {user_input.get('property_zip')}
Property Address: {user_input.get('property_address')}
Annual Income: {annual_income}
Purchase Price: {purchase_price}
Down Payment: {down_payment}
Loan Purpose: {user_input.get('loan_purpose')}

Financial Analysis (Derived from Plaid):
Monthly Income: {monthly_income}
Down Payment Percentage: {down_payment_percentage}%
Liquid Assets: {liquid_assets}
"""

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=5
            )

            result = response.choices[0].message.content.strip().lower()
            if result not in ["approve", "disapprove"]:
                return "disapprove"
            return result

        except Exception as e:
            print(f"Error in PreApprovalEngine: {e}")
            return "disapprove"
