from environs import Env

env = Env()
env.read_env()
TOKEN = env.str("TOKEN")
PSNR_THRESHOLD = env.int("PSNR_THRESHOLD")
IMAGE_DIR = env.path("IMAGE_DIR")
DB_CONNECTION = env.str("DB_CONNECTION")
DB_ECHO = env.bool("DB_ECHO", False)
