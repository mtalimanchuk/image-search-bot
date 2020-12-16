from environs import Env

env = Env()
env.read_env()
TOKEN = env.str("TOKEN")
PSNR_TRESHOLD = env.int("PSNR_TRESHOLD")
IMAGE_DIR = env.path("IMAGE_DIR")
DB_CONNECTION = env.str("DB_CONNECTION")
DB_ECHO = env.bool("DB_ECHO", False)
