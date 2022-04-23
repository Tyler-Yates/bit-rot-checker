########################
# Configurable constants
########################
# The file on disk to save information about how recently a file has been scanned.
RECENCY_FILE_NAME = "recency.pickle"

# How many days to wait before checking a file again.
# This threshold is ignored if the file modified time has changed.
# Lower this to scan files more frequently.
RECENCY_MINIMUM_AGE_DAYS = 90

# The file on disk to load configuration from.
CONFIG_FILE_NAME = "config.json"

# The chunk size for calculating the checksum.
# This affects the performance when reading your disk.
CHUNK_SIZE = 4096 * 1024

# Prefix strings to skip when processing files.
# Each prefix is evaluated for every part of the path.
# For example [".st"] means that C:\Program Files\MyProgram\.stver\test.txt would be skipped
SKIP_PREFIXES = [".st"]

########################
# Mongo constants
########################
# DO NOT modify these constants as they are fields in the database.
MONGO_ID_KEY = "_id"
FILE_ID_KEY = "file_id"
MODIFIED_TIME_KEY = "mtime"
SIZE_KEY = "size"
CHECKSUM_KEY = "checksum"
LAST_ACCESSED_KEY = "last_accessed"

# Use 366 days in a year to round up
SECONDS_IN_A_YEAR = 60 * 60 * 24 * 366
