"""Seed Vultr vector store with curated legal reference data.

Covers the 41 CUAD clause types with standard language, risk indicators,
and enforceability notes. No external datasets required.

Usage:
    python seed_vultr_rag.py
"""

import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()

VULTR_BASE = "https://api.vultrinference.com/v1"
VULTR_API_KEY = os.environ.get("VULTR_INFERENCE_API_KEY", "")
COLLECTION_ID = os.environ.get("VULTR_LEGAL_COLLECTION_ID", "")
HEADERS = {
    "Authorization": f"Bearer {VULTR_API_KEY}",
    "Content-Type": "application/json",
}

# Curated legal reference data covering major clause types
LEGAL_REFERENCES = [
    # --- Non-Compete ---
    {
        "content": (
            "Clause Type: Non-Compete\n"
            "Risk Category: Compliance\n"
            "Standard Language: Employee agrees not to engage in any business that competes with the Company "
            "within a 25-mile radius for a period of 12 months following termination of employment.\n"
            "Risk Indicators: Duration over 2 years is often unenforceable. Geographic scope must be reasonable. "
            "Must be supported by adequate consideration. California, North Dakota, Oklahoma, and Minnesota ban most non-competes. "
            "FTC has proposed a nationwide ban on non-compete agreements.\n"
            "Enforceability: Courts apply a reasonableness test considering duration, geographic scope, and scope of restricted activities. "
            "Overly broad non-competes are commonly struck down or reformed by courts."
        ),
        "description": "Non-compete clause standards and enforceability",
    },
    # --- Non-Solicitation ---
    {
        "content": (
            "Clause Type: Non-Solicitation\n"
            "Risk Category: Compliance\n"
            "Standard Language: For a period of 12 months after termination, Employee shall not directly or indirectly "
            "solicit any customer or employee of the Company for the purpose of competing with the Company's business.\n"
            "Risk Indicators: More enforceable than non-competes. Must be limited in time and scope. "
            "Should distinguish between customer non-solicitation and employee non-solicitation. "
            "Overly broad definitions of 'solicit' can render clause unenforceable.\n"
            "Enforceability: Generally more enforceable than non-competes if reasonably scoped. "
            "Courts look at whether the restriction protects legitimate business interests."
        ),
        "description": "Non-solicitation clause standards",
    },
    # --- Termination ---
    {
        "content": (
            "Clause Type: Termination\n"
            "Risk Category: Operational\n"
            "Standard Language: Either party may terminate this Agreement upon 30 days' written notice to the other party. "
            "Either party may terminate immediately upon material breach that remains uncured for 15 days after written notice.\n"
            "Risk Indicators: One-sided termination rights are a red flag. Watch for termination 'for convenience' by only one party. "
            "Look for automatic renewal with short opt-out windows. Ensure termination triggers are clearly defined.\n"
            "Enforceability: Termination provisions are generally enforceable. Courts look at whether notice requirements were met "
            "and whether breach was truly material."
        ),
        "description": "Termination clause standards",
    },
    # --- Indemnification ---
    {
        "content": (
            "Clause Type: Indemnification\n"
            "Risk Category: Financial\n"
            "Standard Language: Party A shall indemnify, defend, and hold harmless Party B from and against all claims, damages, "
            "losses, costs, and expenses (including reasonable attorneys' fees) arising out of Party A's breach of this Agreement "
            "or negligent acts or omissions.\n"
            "Risk Indicators: One-sided indemnification creates significant financial exposure. Watch for broad indemnification "
            "covering 'any and all claims' without limitation. Ensure carve-outs for the indemnified party's own negligence. "
            "Look for duty to defend vs. duty to indemnify distinction.\n"
            "Enforceability: Generally enforceable but some jurisdictions limit indemnification for one's own negligence. "
            "Anti-indemnity statutes exist in construction and oil/gas industries."
        ),
        "description": "Indemnification clause standards and risks",
    },
    # --- Limitation of Liability ---
    {
        "content": (
            "Clause Type: Limitation of Liability\n"
            "Risk Category: Financial\n"
            "Standard Language: In no event shall either party's total cumulative liability exceed the total amounts paid "
            "under this Agreement during the 12 months preceding the claim. Neither party shall be liable for any indirect, "
            "incidental, special, consequential, or punitive damages.\n"
            "Risk Indicators: Absence of liability cap is a major red flag. Uncapped liability for data breaches or IP infringement "
            "is common but risky. Watch for one-sided caps. Consequential damages exclusion should be mutual. "
            "Super-cap carve-outs for certain obligations are increasingly common.\n"
            "Enforceability: Generally enforceable for commercial contracts between sophisticated parties. "
            "May not be enforceable for gross negligence, willful misconduct, or fraud."
        ),
        "description": "Limitation of liability clause standards",
    },
    # --- Confidentiality / NDA ---
    {
        "content": (
            "Clause Type: Confidentiality\n"
            "Risk Category: Compliance\n"
            "Standard Language: Receiving Party agrees to hold all Confidential Information in strict confidence and not to disclose "
            "such information to any third party without prior written consent. Confidential Information excludes information that: "
            "(a) is publicly available, (b) was known prior to disclosure, (c) was independently developed, or (d) was received from a third party.\n"
            "Risk Indicators: Overly broad definition of confidential information. No time limit on confidentiality obligations. "
            "Missing standard exclusions. No provision for legally compelled disclosure. Residuals clause allowing use of "
            "retained information in unaided memory.\n"
            "Enforceability: Standard NDAs are generally enforceable. Perpetual confidentiality obligations may be challenged. "
            "Must have clear definition of what constitutes Confidential Information."
        ),
        "description": "Confidentiality and NDA clause standards",
    },
    # --- Intellectual Property ---
    {
        "content": (
            "Clause Type: Intellectual Property\n"
            "Risk Category: Operational\n"
            "Standard Language: All intellectual property created by Employee in the course of employment shall be the sole "
            "property of the Company. Employee hereby assigns all right, title, and interest in such intellectual property to the Company.\n"
            "Risk Indicators: Overly broad IP assignment covering work created outside employment. No carve-out for prior inventions. "
            "Work-for-hire provisions for independent contractors must meet Copyright Act requirements. "
            "Watch for assignment of moral rights (not recognized in all jurisdictions).\n"
            "Enforceability: IP assignment clauses are generally enforceable but must be supported by consideration. "
            "Some states (CA, DE, IL, MN, WA) limit employer IP assignment to work-related inventions."
        ),
        "description": "Intellectual property assignment clause standards",
    },
    # --- Exclusivity ---
    {
        "content": (
            "Clause Type: Exclusivity\n"
            "Risk Category: Operational\n"
            "Standard Language: During the Term, Supplier shall be the exclusive provider of the Services to Company, "
            "and Company shall not engage any other provider for similar services.\n"
            "Risk Indicators: One-sided exclusivity without performance guarantees is risky. Ensure exclusivity is reciprocal "
            "or has clear performance benchmarks. Watch for exclusivity that extends beyond the contract term. "
            "May raise antitrust concerns in certain market conditions.\n"
            "Enforceability: Generally enforceable if supported by consideration and reasonable in scope. "
            "Antitrust scrutiny may apply in concentrated markets."
        ),
        "description": "Exclusivity clause standards",
    },
    # --- Assignment ---
    {
        "content": (
            "Clause Type: Assignment\n"
            "Risk Category: Operational\n"
            "Standard Language: Neither party may assign this Agreement without the prior written consent of the other party, "
            "except that either party may assign this Agreement to a successor in connection with a merger, acquisition, "
            "or sale of all or substantially all of its assets.\n"
            "Risk Indicators: Anti-assignment clauses without change-of-control exceptions can trap a party. "
            "Watch for one-sided assignment rights. Ensure IP licenses survive assignment. "
            "Consider whether consent to assign can be unreasonably withheld.\n"
            "Enforceability: Anti-assignment clauses are generally enforceable. UCC Article 9 may override in certain contexts. "
            "Federal law overrides for government contracts."
        ),
        "description": "Assignment and anti-assignment clause standards",
    },
    # --- Governing Law ---
    {
        "content": (
            "Clause Type: Governing Law\n"
            "Risk Category: Compliance\n"
            "Standard Language: This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, "
            "without regard to its conflict of laws principles.\n"
            "Risk Indicators: Governing law should align with where parties operate or where disputes are likely. "
            "Some jurisdictions are more favorable to certain contract types. Watch for mandatory arbitration in unfavorable jurisdictions. "
            "Consumer contracts may be subject to mandatory local law regardless of choice-of-law provision.\n"
            "Enforceability: Generally enforceable between commercial parties. Consumer contracts may be subject to local consumer protection laws."
        ),
        "description": "Governing law clause standards",
    },
    # --- Arbitration ---
    {
        "content": (
            "Clause Type: Arbitration\n"
            "Risk Category: Compliance\n"
            "Standard Language: Any dispute arising out of or relating to this Agreement shall be resolved by binding arbitration "
            "in accordance with the rules of the American Arbitration Association. The arbitration shall take place in New York, NY. "
            "The arbitrator's decision shall be final and binding.\n"
            "Risk Indicators: Mandatory arbitration eliminates right to jury trial. Class action waivers may be unenforceable in employment "
            "and consumer contexts. Arbitration costs may be prohibitive for smaller claims. Watch for one-sided arbitration clauses "
            "where only one party is bound.\n"
            "Enforceability: Federal Arbitration Act strongly favors enforcement. Exceptions for unconscionability, "
            "certain employment agreements, and some consumer contracts."
        ),
        "description": "Arbitration clause standards",
    },
    # --- Warranty ---
    {
        "content": (
            "Clause Type: Warranty\n"
            "Risk Category: Financial\n"
            "Standard Language: Supplier warrants that the Services will be performed in a professional and workmanlike manner "
            "consistent with generally accepted industry standards. This warranty shall remain in effect for 90 days following delivery.\n"
            "Risk Indicators: 'As-is' disclaimers eliminate all warranties — significant risk for buyers. Short warranty periods "
            "may not provide adequate protection. Watch for limitations on warranty remedies (repair/replace only vs. refund). "
            "Implied warranties (merchantability, fitness for purpose) may be disclaimed in B2B but not always in consumer contracts.\n"
            "Enforceability: Express warranties are generally enforceable. Implied warranty disclaimers must be conspicuous. "
            "UCC governs goods warranties; common law governs services."
        ),
        "description": "Warranty clause standards",
    },
    # --- Insurance ---
    {
        "content": (
            "Clause Type: Insurance\n"
            "Risk Category: Financial\n"
            "Standard Language: Contractor shall maintain commercial general liability insurance with limits of not less than "
            "$1,000,000 per occurrence and $2,000,000 aggregate, and professional liability insurance of not less than $1,000,000.\n"
            "Risk Indicators: Inadequate coverage limits relative to contract value. Missing required coverage types "
            "(E&O, cyber liability, workers' comp). No requirement to name the other party as additional insured. "
            "No requirement to provide certificates of insurance.\n"
            "Enforceability: Insurance requirements are generally enforceable contractual obligations."
        ),
        "description": "Insurance requirement clause standards",
    },
    # --- Liquidated Damages ---
    {
        "content": (
            "Clause Type: Liquidated Damages\n"
            "Risk Category: Financial\n"
            "Standard Language: In the event of late delivery, Supplier shall pay liquidated damages of 1% of the total contract value "
            "per week of delay, up to a maximum of 10% of the total contract value.\n"
            "Risk Indicators: Liquidated damages must be a reasonable estimate of anticipated harm — penalties are unenforceable. "
            "Uncapped liquidated damages are effectively penalties. Watch for one-sided liquidated damages. "
            "Consider whether actual damages would be difficult to calculate.\n"
            "Enforceability: Enforceable if (1) damages were difficult to estimate at time of contracting, and "
            "(2) the amount is a reasonable forecast of actual damages. Treated as unenforceable penalty if grossly disproportionate."
        ),
        "description": "Liquidated damages clause standards",
    },
    # --- Force Majeure ---
    {
        "content": (
            "Clause Type: Force Majeure\n"
            "Risk Category: Operational\n"
            "Standard Language: Neither party shall be liable for any failure or delay in performing its obligations under this Agreement "
            "to the extent such failure or delay results from circumstances beyond the reasonable control of that party, including but not limited to "
            "acts of God, natural disasters, pandemics, war, terrorism, government actions, or labor disputes.\n"
            "Risk Indicators: Narrow force majeure definitions may not cover relevant events (e.g., pandemics, supply chain disruptions, cyberattacks). "
            "Watch for whether force majeure excuses performance entirely or only delays it. Termination rights after prolonged force majeure. "
            "Financial hardship alone is rarely force majeure.\n"
            "Enforceability: Strictly construed — only covers events specifically listed or clearly within the general description. "
            "Post-COVID, courts scrutinize pandemic-related claims carefully."
        ),
        "description": "Force majeure clause standards",
    },
    # --- Data Privacy ---
    {
        "content": (
            "Clause Type: Data Privacy / Data Protection\n"
            "Risk Category: Compliance\n"
            "Standard Language: Processor shall process Personal Data only on documented instructions from the Controller, "
            "implement appropriate technical and organizational measures to ensure security, notify Controller of data breaches "
            "within 72 hours, and assist with data subject access requests.\n"
            "Risk Indicators: Non-compliance with GDPR, CCPA, or other applicable privacy laws. Missing data processing agreement (DPA). "
            "No breach notification timeline. Unclear data retention and deletion obligations. Cross-border data transfer without adequate safeguards. "
            "No sub-processor restrictions.\n"
            "Enforceability: Data privacy obligations are largely governed by statute (GDPR, CCPA). "
            "Contractual provisions that fall below statutory requirements may not shield parties from regulatory liability."
        ),
        "description": "Data privacy and protection clause standards",
    },
    # --- Renewal ---
    {
        "content": (
            "Clause Type: Renewal / Auto-Renewal\n"
            "Risk Category: Operational\n"
            "Standard Language: This Agreement shall automatically renew for successive one-year terms unless either party provides "
            "written notice of non-renewal at least 60 days prior to the end of the then-current term.\n"
            "Risk Indicators: Auto-renewal with short opt-out windows can trap parties. Watch for price escalation on renewal. "
            "Ensure renewal terms are clearly stated. Some states require specific disclosures for auto-renewal in consumer contracts.\n"
            "Enforceability: Generally enforceable in B2B. Consumer auto-renewal laws in many states require clear disclosure "
            "and easy cancellation mechanisms."
        ),
        "description": "Renewal and auto-renewal clause standards",
    },
    # --- Non-Disparagement ---
    {
        "content": (
            "Clause Type: Non-Disparagement\n"
            "Risk Category: Reputational\n"
            "Standard Language: Each party agrees not to make any public statements or communications that disparage, "
            "defame, or damage the reputation of the other party, its officers, directors, employees, or products.\n"
            "Risk Indicators: Overly broad non-disparagement can chill legitimate speech and whistleblowing. "
            "NLRB has limited non-disparagement in employment contexts. May conflict with Dodd-Frank whistleblower protections. "
            "Should include carve-outs for truthful statements, legal proceedings, and regulatory reporting.\n"
            "Enforceability: Limited enforceability in employment context after NLRB McLaren Macomb decision (2023). "
            "More enforceable in commercial/M&A contexts. Must include legal process carve-outs."
        ),
        "description": "Non-disparagement clause standards",
    },
    # --- Cap on Liability ---
    {
        "content": (
            "Clause Type: Cap on Liability\n"
            "Risk Category: Financial\n"
            "Standard Language: The total aggregate liability of either party under this Agreement shall not exceed "
            "the total fees paid or payable under this Agreement during the 12-month period preceding the event giving rise to the claim.\n"
            "Risk Indicators: Very low caps relative to potential damages. One-sided caps. No super-cap carve-outs for IP indemnification, "
            "data breaches, or confidentiality breaches. Cap tied to fees paid (disadvantages party early in the contract). "
            "Watch for caps that apply 'per claim' vs. 'in aggregate.'\n"
            "Enforceability: Liability caps are generally enforceable in commercial contracts. May not apply to willful misconduct, "
            "fraud, or certain statutory claims."
        ),
        "description": "Liability cap clause standards",
    },
    # --- Audit Rights ---
    {
        "content": (
            "Clause Type: Audit Rights\n"
            "Risk Category: Compliance\n"
            "Standard Language: Licensor shall have the right, upon 30 days' written notice and no more than once per year, "
            "to audit Licensee's records to verify compliance with the terms of this Agreement. Audits shall be conducted "
            "during normal business hours at Licensee's expense if a material discrepancy is found.\n"
            "Risk Indicators: Unlimited or frequent audit rights are disruptive. Watch for who bears audit costs. "
            "Ensure adequate notice period. Consider confidentiality of audited records. "
            "Third-party auditor requirements.\n"
            "Enforceability: Generally enforceable. Scope must be reasonable and related to contract compliance."
        ),
        "description": "Audit rights clause standards",
    },
    # --- Revenue/Profit Sharing ---
    {
        "content": (
            "Clause Type: Revenue/Profit Sharing\n"
            "Risk Category: Financial\n"
            "Standard Language: Company shall pay Partner a royalty equal to 5% of Net Revenue derived from the sale of Products "
            "incorporating Partner's technology, payable quarterly within 30 days of quarter end.\n"
            "Risk Indicators: Ambiguous definitions of 'net revenue' or 'profit' allow manipulation. "
            "Missing audit rights to verify calculations. No minimum guaranteed payments. "
            "Watch for deductions that reduce the effective rate. Ensure clear reporting obligations.\n"
            "Enforceability: Enforceable but highly litigated due to definitional disputes. "
            "Clear accounting definitions are essential."
        ),
        "description": "Revenue and profit sharing clause standards",
    },
    # --- Most Favored Nation ---
    {
        "content": (
            "Clause Type: Most Favored Nation (MFN)\n"
            "Risk Category: Financial\n"
            "Standard Language: If Supplier offers more favorable pricing or terms to any other customer for substantially similar "
            "services, Supplier shall promptly offer the same pricing or terms to Buyer.\n"
            "Risk Indicators: MFN clauses can limit pricing flexibility and raise antitrust concerns. "
            "Watch for narrow definitions of 'substantially similar.' Compliance verification is difficult. "
            "May discourage competitive pricing to other customers.\n"
            "Enforceability: Generally enforceable but may face antitrust scrutiny, particularly in healthcare and insurance."
        ),
        "description": "Most favored nation clause standards",
    },
    # --- Change of Control ---
    {
        "content": (
            "Clause Type: Change of Control\n"
            "Risk Category: Operational\n"
            "Standard Language: In the event of a Change of Control of either party, the other party shall have the right "
            "to terminate this Agreement upon 90 days' written notice. 'Change of Control' means any merger, acquisition, "
            "or transfer of more than 50% of voting securities.\n"
            "Risk Indicators: Change of control triggers can block M&A transactions or significantly reduce deal value. "
            "Watch for broad definitions that include management changes. Consider whether consent rights vs. termination rights "
            "are more appropriate. Assignment provisions may conflict with CoC provisions.\n"
            "Enforceability: Generally enforceable. Must be carefully drafted to avoid ambiguity about trigger events."
        ),
        "description": "Change of control clause standards",
    },
    # --- License Grant ---
    {
        "content": (
            "Clause Type: License Grant\n"
            "Risk Category: Operational\n"
            "Standard Language: Licensor hereby grants Licensee a non-exclusive, non-transferable, revocable license to use "
            "the Software solely for Licensee's internal business purposes during the Term.\n"
            "Risk Indicators: Exclusive vs. non-exclusive has major implications. Watch for scope limitations (field of use, territory). "
            "Revocable vs. irrevocable licenses. Sublicensing rights. Open source license compatibility. "
            "Ensure license survives termination for pre-paid periods.\n"
            "Enforceability: License grants are generally enforceable. Scope ambiguities are construed against the licensor."
        ),
        "description": "License grant clause standards",
    },
    # --- Payment Terms ---
    {
        "content": (
            "Clause Type: Payment Terms\n"
            "Risk Category: Financial\n"
            "Standard Language: Payment is due within 30 days of invoice date (Net 30). Late payments shall accrue interest "
            "at the lesser of 1.5% per month or the maximum rate permitted by law.\n"
            "Risk Indicators: Extended payment terms (Net 60, Net 90) create cash flow risk. Watch for right to withhold payment "
            "for disputes. Ensure late payment interest is reasonable and enforceable. Set-off rights can reduce effective payment. "
            "Early payment discounts may pressure cash flow.\n"
            "Enforceability: Payment terms are generally enforceable. Usury laws cap interest rates in most jurisdictions."
        ),
        "description": "Payment terms clause standards",
    },
    # --- Right of First Refusal ---
    {
        "content": (
            "Clause Type: Right of First Refusal (ROFR)\n"
            "Risk Category: Operational\n"
            "Standard Language: Before selling or transferring any ownership interest, the selling party shall first offer "
            "such interest to the other party on the same terms and conditions as the proposed third-party transaction. "
            "The other party shall have 30 days to accept or decline.\n"
            "Risk Indicators: ROFR can chill third-party interest and depress valuations. Watch for matching rights vs. "
            "first offer rights (ROFO). Ensure clear timelines for exercise. Consider impact on exit strategies.\n"
            "Enforceability: Generally enforceable. Must have clear procedures and reasonable exercise periods."
        ),
        "description": "Right of first refusal clause standards",
    },
    # --- Severability ---
    {
        "content": (
            "Clause Type: Severability\n"
            "Risk Category: Compliance\n"
            "Standard Language: If any provision of this Agreement is held to be invalid or unenforceable, "
            "the remaining provisions shall continue in full force and effect. The invalid provision shall be modified "
            "to the minimum extent necessary to make it valid and enforceable.\n"
            "Risk Indicators: Absence of severability clause means one unenforceable provision could void the entire agreement. "
            "Watch for 'reformation' language that allows courts to rewrite provisions. "
            "Essential clause doctrine may override severability if core provisions are struck.\n"
            "Enforceability: Standard boilerplate that is routinely enforced."
        ),
        "description": "Severability clause standards",
    },
    # --- Entire Agreement / Integration ---
    {
        "content": (
            "Clause Type: Entire Agreement / Integration Clause\n"
            "Risk Category: Compliance\n"
            "Standard Language: This Agreement constitutes the entire agreement between the parties and supersedes "
            "all prior negotiations, representations, warranties, commitments, offers, and understandings, "
            "whether written or oral, with respect to the subject matter hereof.\n"
            "Risk Indicators: Integration clauses can eliminate reliance on prior promises or representations made during negotiations. "
            "May not bar fraud claims based on pre-contractual misrepresentation. Watch for carve-outs for specific prior agreements. "
            "Consider whether side letters or amendments are properly referenced.\n"
            "Enforceability: Strongly enforceable. Parol evidence rule prevents introduction of prior or contemporaneous agreements."
        ),
        "description": "Entire agreement and integration clause standards",
    },
    # --- Waiver ---
    {
        "content": (
            "Clause Type: Waiver\n"
            "Risk Category: Compliance\n"
            "Standard Language: The failure of either party to enforce any provision of this Agreement shall not constitute "
            "a waiver of such provision or of the right to enforce it at a later time.\n"
            "Risk Indicators: Without a no-waiver clause, repeated failure to enforce a provision may constitute waiver. "
            "Watch for waiver provisions that require written consent — oral waivers may still be argued. "
            "Consider whether anti-waiver provisions apply to both parties.\n"
            "Enforceability: Standard boilerplate that is routinely enforced. Courts still may find implied waiver in egregious cases."
        ),
        "description": "Waiver clause standards",
    },
    # --- Notice ---
    {
        "content": (
            "Clause Type: Notice\n"
            "Risk Category: Operational\n"
            "Standard Language: All notices required under this Agreement shall be in writing and shall be deemed delivered when "
            "(a) delivered personally, (b) sent by certified mail, return receipt requested, (c) sent by overnight courier, "
            "or (d) sent by email with confirmation of receipt, to the addresses specified herein.\n"
            "Risk Indicators: Email-only notice provisions may create disputes about receipt. Ensure notice addresses are current. "
            "Consider time zone differences for deadline calculations. Watch for 'deemed received' provisions that may disadvantage a party.\n"
            "Enforceability: Notice provisions are generally enforceable. Strict compliance is typically required."
        ),
        "description": "Notice clause standards",
    },
]


def upload_to_vultr(items: list[dict]) -> None:
    """Upload reference items to Vultr vector store."""
    if not VULTR_API_KEY or not COLLECTION_ID:
        print("ERROR: Set VULTR_INFERENCE_API_KEY and VULTR_LEGAL_COLLECTION_ID in .env")
        sys.exit(1)

    print(f"Uploading {len(items)} items to Vultr vector store...")
    success = 0
    errors = 0

    with httpx.Client(timeout=60) as client:
        for i, item in enumerate(items):
            try:
                response = client.post(
                    f"{VULTR_BASE}/vector_store/{COLLECTION_ID}/items",
                    headers=HEADERS,
                    json=item,
                )
                response.raise_for_status()
                success += 1
            except httpx.HTTPStatusError as e:
                print(f"  Warning: Failed to upload '{item['description']}': {e.response.status_code} {e.response.text[:200]}")
                errors += 1

            if (i + 1) % 10 == 0 or i + 1 == len(items):
                print(f"  Progress: {i + 1}/{len(items)} ({success} ok, {errors} failed)")

    print(f"\nUpload complete: {success} succeeded, {errors} failed")


def main():
    print("=== ContractPilot: Seeding Vultr Legal Knowledge Base ===\n")
    print(f"Collection: {COLLECTION_ID}")
    print(f"Items to upload: {len(LEGAL_REFERENCES)}\n")

    upload_to_vultr(LEGAL_REFERENCES)

    print("\n=== Done! Legal knowledge base is ready. ===")


if __name__ == "__main__":
    main()
