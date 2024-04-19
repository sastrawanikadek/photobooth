from .interfaces import StorageProviderInterface
from .local import LocalStorage

LOCAL_STORAGE_PROVIDER = "local"

DEFAULT_PROVIDERS: dict[str, type[StorageProviderInterface]] = {
    LOCAL_STORAGE_PROVIDER: LocalStorage,
}
