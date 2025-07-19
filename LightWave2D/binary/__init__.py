"""Fallback Python implementations for binary interfaces used in tests."""


class SourceInterface:
    class MultiWavelength:
        def __init__(self, *args, **kwargs):
            pass

        def add_to_field(self, *args, **kwargs):
            pass


class fdtd_simulation:
    @staticmethod
    def run_fdtd(**kwargs):
        pass

    class Impulsion:
        def __init__(self, *args, **kwargs):
            pass

        def add_to_field(self, *args, **kwargs):
            pass
