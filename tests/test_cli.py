import pytest
import sys
from unittest.mock import patch, MagicMock
from fem4grav.cli import main

def test_cli_missing_file(capsys):
    """Covers the case where no data file is provided (if args.file is None)"""
    #simulate a user running "fem4grav1" without passing a file argument
    with patch.object(sys, 'argv', ['fem4grav']):
        with pytest.raises(SystemExit):  # argparse will force the program to exit
            main()

@patch("fem4grav.cli.run_fem")
@patch("fem4grav.plotting.plot_result")
@patch("fem4grav.cli.save_grid")
@patch("fem4grav.cli.save_table")
@patch("fem4grav.cli.summary")
def test_cli_full_execution(mock_summary, mock_save_table, mock_save_grid, mock_plot, mock_run, tmp_path):
    """Covers the main try block and all export conditions (output, table, plot)"""
    #create a dummy temporary data file for the test
    dummy_file = tmp_path / "dummy_data.txt"
    dummy_file.write_text("fake data")

    #simulate the full command line arguments
    test_args = [
        "fem4grav1", str(dummy_file), 
        "--method", "cubic",
        "--output", "test.npz",
        "--table", "test.txt",
        "--save-plot", "test.png"
    ]

    #inject the simulated arguments into sys.argv
    with patch.object(sys, 'argv', test_args):
        #tell the mocked 'run_fem' to return a dummy object to avoid heavy computations
        mock_run.return_value = MagicMock()
        
        exit_code = main()  #execute the CLI
        
        #verify that execution was successful (return 0) and all export functions were called
        assert exit_code == 0
        mock_run.assert_called_once()
        mock_save_grid.assert_called_once()
        mock_save_table.assert_called_once()
        mock_plot.assert_called_once()

@patch("fem4grav.cli.run_fem")
def test_cli_exception_handling(mock_run, tmp_path, capsys):
    """Covers the except Exception as exc block to ensure errors are caught"""
    dummy_file = tmp_path / "dummy_data.txt"
    dummy_file.write_text("fake data")
    
    with patch.object(sys, 'argv', ["fem4grav", str(dummy_file)]):
        #force the run_fem function to trigger an error (simulating a math/inversion crash)
        mock_run.side_effect = ValueError("Simulated mathematical error")
        
        exit_code = main()

        #the program should exit gracefully and return error code 1
        assert exit_code == 1
        #verify that the error message was printed to stderr
        captured = capsys.readouterr()
        assert "Error: Simulated mathematical error" in captured.err