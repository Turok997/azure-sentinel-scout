from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.consumption import ConsumptionManagementClient

class AzureScanner:
    def __init__(self, subscription_id):
        self.sub_id = subscription_id
        self.credential = DefaultAzureCredential()
        self.storage_client = StorageManagementClient(self.credential, self.sub_id)
        self.compute_client = ComputeManagementClient(self.credential, self.sub_id)
        self.consumption_client = ConsumptionManagementClient(self.credential, self.sub_id)

    def scan_storage(self):
        """checks for storage account issues"""
        storage_issues = []
        
        storage_accounts = self.storage_client.storage_accounts.list()
        for sa in storage_accounts:
            # Example check: Ensure HTTPS is required
            if not sa.enable_https_traffic_only:
                storage_issues.append(f"Storage account '{sa.name}' does not require HTTPS traffic.")

        return storage_issues

    def scan_unused_disks(self):
        """checks for unused managed disks"""
        disk_issues = []
        
        disks = self.compute_client.disks.list()
        for d in disks:
            if not d.managed_by:
                disk_issues.append(f"Disk '{d.name}' is not attached to any VM.")

        return disk_issues

    def scan_vm_weekend_status(self):
        """checks if any VMs are running during the weekend"""
        # only relevant if today is Saturday (5) or Sunday (6)
        is_weekend = datetime.now().weekday() >= 5
        vm_issues = []
        
        vms = self.compute_client.virtual_machines.list_all()
        for vm in vms:
            # checks if instance is running
            status = self.compute_client.virtual_machines.instance_view(
                self._get_rg_from_id(vm.id), vm.name)
            
            for s in status.statuses:
                if s.code == "PowerState/running" and is_weekend:
                    vm_issues.append(f"VM '{vm.name}' runs on weekends - consider shutting it down to save costs.")
        return vm_issues

    def get_monthly_costs(self):
        """Queries the monthly costs."""
        now = datetime.now()
        start_date = (now - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = now.strftime('%Y-%m-%d')
        
        # query the costs (Usage Details)
        scope = f"/subscriptions/{self.sub_id}"
        usage = self.consumption_client.usage_details.list(scope)
        
        total_cost = 0
        for item in usage:
            # Modern API uses 'amount', Legacy API uses 'pretax_cost'
            # We use getattr to safely check for both
            cost = getattr(item, 'amount', getattr(item, 'pretax_cost', 0))
            total_cost += cost if cost else 0
            
        return round(total_cost, 2)
            
    def _get_rg_from_id(self, resource_id):
        return resource_id.split("/")[4]