import os

from scanners import AzureScanner
from notifier import EmailNotifier

SUBSCRIPTION_ID = os.getenv("SUBSCRIPTION_ID")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PW = os.getenv("GMAIL_APP_PW")

# --- CONFIGURATION ---
SUBSCRIPTION_ID = "5938a704-c45d-4530-b74f-08e73df1cb38"
GMAIL_USER = "jantissen1@gmail.com"
GMAIL_APP_PW = "lqky bgda qayo zpox"

def main():
    # 1. Initialize tools
    scanner = AzureScanner(SUBSCRIPTION_ID)
    notifier = EmailNotifier(GMAIL_USER, GMAIL_APP_PW)

    # 2. Run Scans
    print("--- Starting Azure Sentinel Scout ---")
    storage_issues = scanner.scan_storage()
    disk_issues = scanner.scan_unused_disks()
    cost = scanner.get_monthly_costs()
    vm_issues = scanner.scan_vm_weekend_status()

    # Combine all findings
    all_findings = storage_issues + disk_issues + vm_issues

    # 3. Handle Results
    if all_findings:
        print(f"[*] Found {len(all_findings)} issues. Sending report...")
        notifier.send_report(GMAIL_USER, all_findings, cost)
    else:
        print("[+] No issues found. Your environment is clean!")

if __name__ == "__main__":
    main()