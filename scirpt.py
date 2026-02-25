import csv
from dataclasses import dataclass
from typing import List

@dataclass
class Asset:
    name: str
    quantity: str
    serial_number: str
    location: str
    comments: str
    manufacturer: str
    supplier: str
    asset_type: str
    assigned_to: str
    company: str
    mac_wired: str
    mac_wireless: str
    purchase_date: str
    warranty_expire: str
    notes: str
    owner: str

@dataclass
class NonComplianceData:
    DeviceId: str
    IntuneDeviceId: str
    AadDeviceId: str
    PartnerDeviceId: str
    DeviceName: str
    DeviceType: str 
    OSDescription: str
    OSVersion: str
    OwnerType: str
    OwnerType_loc: str
    LastContact: str
    InGracePeriodUntil: str
    IMEI: str
    SerialNumber: str 
    PrimaryUser: str
    UserId: str
    UPN: str
    UserEmail: str
    UserName: str
    DeviceHealthThreatLevel: str
    DeviceHealthThreatLevel_loc: str
    RetireAfterDatetime: str
    ComplianceState: str
    ComplianceState_loc: str
    OS: str 
    OS_loc: str

class DataManager:
    NonComplianceList: List[NonComplianceData] = []
    AssetData: List[Asset] = []

    @classmethod
    def load_data(cls, file_path):
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            first_line = file.readline()
            # Fixed typo: changed 'seq=' to 'sep='
            if not first_line.startswith('sep='):
                file.seek(0)

            reader = csv.DictReader(file)
            reader.fieldnames = [name.strip() for name in reader.fieldnames]
            
            if file_path == 'noncompliance.csv':
                for row in reader:
                    item = NonComplianceData(**row) 
                    cls.NonComplianceList.append(item)
            
            elif file_path == 'assets.csv':
                for row in reader:
                    # Fixed: Added the column keys back into the .get() methods
                    item = Asset(
                        name=row.get('Name', 'N/A'),
                        quantity=row.get('Quantity', '0'),
                        serial_number=row.get('SerialNumber', 'N/A'),
                        location=row.get('Location', 'N/A'),
                        comments=row.get('Comments', ''),
                        manufacturer=row.get('Manufacturer', 'N/A'),
                        supplier=row.get('Supplier', 'N/A'),
                        asset_type=row.get('Type', 'N/A'),
                        assigned_to=row.get('Assigned To', 'N/A'),
                        company=row.get('Company', 'N/A'),
                        mac_wired=row.get('MAC - Wired', 'N/A'),
                        mac_wireless=row.get('MAC - Wireless', 'N/A'),
                        purchase_date=row.get('Purchase Date', 'N/A'),
                        warranty_expire=row.get('Warranty Expire', 'N/A'),
                        notes=row.get('Additional Notes', ''),
                        owner=row.get('Owner', 'N/A')
                    )
                    cls.AssetData.append(item)

    @classmethod
    def generate_report(cls, output_file='Compliance_Report.txt'):
        # CASE INSENSITIVE: Normalize serials to uppercase and strip spaces
        non_compliant_sns = {
            device.SerialNumber.strip().upper() 
            for device in cls.NonComplianceList if device.SerialNumber
        }
        
        asset_sns = {
            asset.serial_number.strip().upper() 
            for asset in cls.AssetData if asset.serial_number
        }

        with open(output_file, mode='w', encoding='utf-8') as f:
            f.write("COMPLIANCE AUDIT REPORT\n")
            f.write("="*40 + "\n\n")

            # SECTION 1: Matches (Found in Assets but marked Non-Compliant in Intune)
            f.write("--- NON-COMPLIANT ASSETS FOUND IN DATABASE ---\n")
            match_count = 0
            for asset in cls.AssetData:
                sn_clean = asset.serial_number.strip().upper()
                if sn_clean in non_compliant_sns:
                    f.write(f"MATCH: {asset.name} | SN: {asset.serial_number} | User: {asset.assigned_to}\n")
                    match_count += 1
            
            # SECTION 2: Missing (Found in Intune but NOT found in Assets.csv)
            f.write("\n--- INTUNE DEVICES MISSING FROM ASSET DATABASE ---\n")
            missing_count = 0
            for device in cls.NonComplianceList:
                sn_clean = device.SerialNumber.strip().upper()
                if sn_clean and sn_clean not in asset_sns:
                    f.write(f"MISSING: {device.DeviceName} | SN: {device.SerialNumber} | User: {device.UserName}\n")
                    missing_count += 1
            
            f.write("\n" + "="*40 + "\n")
            f.write(f"Total Non-Compliant Matches: {match_count}\n")
            f.write(f"Total Devices Missing from Inventory: {missing_count}\n")
        
        print(f"Report successfully generated: {output_file}")

# Execution
DataManager.load_data('noncompliance.csv')
DataManager.load_data('assets.csv')
DataManager.generate_report()