from varfish_cli.ftypes.ftypes import FileType, guess_by_path


def test_guess_by_path():
    assert guess_by_path("file.md5") == FileType.MD5
    assert guess_by_path("file.bam") == FileType.BAM
    assert guess_by_path("file.xyz") == FileType.UNKNOWN
