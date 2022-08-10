from mypy.plugin import Plugin


class StrongtypingPlugin(Plugin):
    def get_type_analyze_hook(self, fullname: str):
        if "strongtyping.types" in fullname:
            return strongtyping_to_type_hook
        return None


def plugin(version: str):
    # ignore version argument if the plugin works with all mypy versions.
    return StrongtypingPlugin


def strongtyping_to_type_hook(ctx):
    return ctx.api.named_type("builtins.type", [])
