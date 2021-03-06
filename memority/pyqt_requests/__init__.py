# region GET requests
from .check_client_contract_updates_request import CheckClientContractUpdatesRequest
from .get_box_dir import GetBoxDirRequest
from .check_app_updates import CheckAppUpdatesRequest
from .get_space_for_hosting import GetDiskSpaceForHostingRequest
from .get_space_used import GetSpaceUsedRequest
from .get_sync_status import GetSyncStatusRequest
from .get_user_address import GetUserAddressRequest
from .get_user_balance import GetUserBalanceRequest
from .get_user_files import GetUserFilesRequest
from .get_user_ip import GetUserIPRequest
from .get_user_role import GetUserRoleRequest
from .get_user_transactions import GetUserTransactionsRequest
from .get_file_metadata import GetFileMetadataRequest
from .ping import PingRequest
# endregion

# region POST requests
from .change_box_dir import ChangeBoxDirRequest
from .create_renter_account import CreateRenterAccountRequest
from .create_hoster_account import CreateHosterAccountRequest
from .export_account import ExportAccountRequest
from .generate_address import GenerateAddressRequest
from .import_account import ImportAccountRequest
from .prolong_deposit_for_file import ProlongDepositForFileRequest
from .request_mmr import RequestMMRRequest
from .send_miner_request import MinerStatusRequest
from .set_disk_space_for_hosting import SetDiskSpaceForHostingRequest
# endregion
