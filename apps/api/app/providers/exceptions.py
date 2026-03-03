class ProviderError(Exception):
    pass


class ProviderTimeoutError(ProviderError):
    pass


class ProviderNotFoundError(ProviderError):
    pass
