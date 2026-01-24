from src import main as main_module


def test_main_prints_hello(capsys):
    main_module.main()
    captured = capsys.readouterr()
    assert "Hello, World!" in captured.out
