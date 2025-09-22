from cafex_core.utils.apache_utils.nifi_process_group_utils import NifiProcessGroupUtils
from cafex_core.utils.apache_utils.apache_air_flow_utils import ApacheAirFlow
from cafex_core.utils.apache_utils.nifi_processor_utils import NifiProcessorUtils


class ApacheUtils(NifiProcessGroupUtils, NifiProcessorUtils, ApacheAirFlow):
    pass
