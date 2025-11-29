"""
Admin sample management utilities
"""
import requests
import json
from datetime import datetime
from utils.helpers import get_backend_url

class AdminSampleManager:
    def __init__(self):
        self.backend_url = get_backend_url()
    
    def get_all_samples_with_validation_status(self):
        """Get all samples including their validation status"""
        try:
            response = requests.get(f"{self.backend_url}/api/admin/samples")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching samples: {e}")
            return []
    
    def validate_sample(self, sample_id, validated=True):
        """Mark a sample as validated or unvalidated"""
        try:
            response = requests.patch(
                f"{self.backend_url}/api/admin/samples/{sample_id}/validate",
                json={"validated": validated}
            )
            response.raise_for_status()
            return {"success": True, "message": "Sample validation status updated"}
        except Exception as e:
            print(f"Error updating sample validation: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_sample(self, sample_id):
        """Delete a sample"""
        try:
            response = requests.delete(f"{self.backend_url}/api/admin/samples/{sample_id}")
            response.raise_for_status()
            return {"success": True, "message": "Sample deleted successfully"}
        except Exception as e:
            print(f"Error deleting sample: {e}")
            return {"success": False, "error": str(e)}
    
    def update_sample(self, sample_id, sample_data):
        """Update sample data"""
        try:
            response = requests.put(
                f"{self.backend_url}/api/admin/samples/{sample_id}",
                json=sample_data
            )
            response.raise_for_status()
            return {"success": True, "message": "Sample updated successfully", "data": response.json()}
        except Exception as e:
            print(f"Error updating sample: {e}")
            return {"success": False, "error": str(e)}
    
    def bulk_validate_samples(self, sample_ids, validated=True):
        """Bulk validate/unvalidate samples"""
        try:
            response = requests.post(
                f"{self.backend_url}/api/admin/samples/bulk-validate",
                json={"sample_ids": sample_ids, "validated": validated}
            )
            response.raise_for_status()
            return {"success": True, "message": f"Bulk validation updated for {len(sample_ids)} samples"}
        except Exception as e:
            print(f"Error bulk validating samples: {e}")
            return {"success": False, "error": str(e)}
    
    def get_sample_statistics(self):
        """Get sample statistics for admin dashboard"""
        try:
            response = requests.get(f"{self.backend_url}/api/admin/statistics")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching statistics: {e}")
            return {
                "total_samples": 0,
                "validated_samples": 0,
                "pending_samples": 0,
                "samples_by_location": {},
                "recent_samples": []
            }

# Global instance
admin_sample_manager = AdminSampleManager()