import hordelib
from loguru import logger

hordelib.initialise()

from horde_model_reference.model_reference_manager import ModelReferenceManager
from hordelib.shared_model_manager import SharedModelManager

from horde_worker_regen.bridge_data.load_config import BridgeDataLoader, reGenBridgeData
from horde_worker_regen.consts import BRIDGE_CONFIG_FILENAME


def main() -> None:
    horde_model_reference_manager = ModelReferenceManager(
        download_and_convert_legacy_dbs=True,
        override_existing=True,
    )

    if not horde_model_reference_manager.download_and_convert_all_legacy_dbs(override_existing=True):
        logger.error("Failed to download and convert legacy DBs. Retrying in 5 seconds...")

    bridge_data: reGenBridgeData
    try:
        bridge_data = BridgeDataLoader.load(
            file_path=BRIDGE_CONFIG_FILENAME,
            horde_model_reference_manager=horde_model_reference_manager,
        )
    except Exception as e:
        logger.error(e)
        input("Press any key to exit...")

    SharedModelManager.load_model_managers()

    if bridge_data.allow_controlnet:
        SharedModelManager.manager.controlnet.download_all_models()

    if bridge_data.allow_post_processing:
        if not SharedModelManager.manager.gfpgan.download_all_models():
            logger.error("Failed to download all GFPGAN models")
        if not SharedModelManager.manager.esrgan.download_all_models():
            logger.error("Failed to download all ESRGAN models")
        if not SharedModelManager.manager.codeformer.download_all_models():
            logger.error("Failed to download all codeformer models")

    for model in bridge_data.image_models_to_load:
        if not SharedModelManager.manager.compvis.download_model(model):
            logger.error(f"Failed to download model {model}")


if __name__ == "__main__":
    main()
