from users.validators.validators import file_validators


class MigrationSafeFileValidators:
    def __init__(self, max_kb, allowed_exts):
        self.max_kb = max_kb
        self.allowed_exts = allowed_exts
        self.validators = file_validators(max_kb, allowed_exts)

    def __call__(self, file_obj):
        for v in self.validators:
            v(file_obj)

    def __repr__(self):
        return (
            f"MigrationSafeFileValidators(max_kb={self.max_kb}, "
            f"allowed_exts={self.allowed_exts})"
        )

    def deconstruct(self):
        return (
            "users.validators.wrappers.MigrationSafeFileValidators",
            (self.max_kb, self.allowed_exts),
            {},
        )
