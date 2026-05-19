from mypy_extensions import mypyc_attr


def bad_class_decorator(cls: type[object]) -> type[object]:
    return cls


@mypyc_attr(native_class=True)
@bad_class_decorator
class MypycNativeSmokeTest:
    def run(self):
        pass