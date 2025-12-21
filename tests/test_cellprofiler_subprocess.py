"""
Test CellProfiler subprocess calls without actually running CellProfiler.

This test verifies that the subprocess.run call is made with the correct
command structure when running CellProfiler headless mode.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestCellProfilerSubprocess(unittest.TestCase):
    """Test that CellProfiler subprocess calls are structured correctly."""
    
    @patch('cellpyability.toolbox._ensure_cellprofiler_path')
    @patch('cellpyability.toolbox.subprocess.run')
    @patch('cellpyability.toolbox.pd.read_csv')
    @patch('cellpyability.toolbox.exit')  # Prevent exit() from terminating the test
    def test_cellprofiler_subprocess_command_structure(self, mock_exit, mock_read_csv, mock_subprocess_run, mock_cp_path):
        """
        Test that the CellProfiler subprocess call uses the correct command structure.
        
        This verifies the command without actually running CellProfiler.
        Expected command: [cp_exe, '-c', '-r', '-p', pipeline, '-i', input, '-o', output]
        """
        # Setup mocks
        mock_cp_path.return_value = '/usr/bin/cellprofiler'
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_read_csv.return_value = MagicMock()
        
        # Import toolbox after patching
        import cellpyability.toolbox as tb
        
        # Create temporary test structure
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            image_dir = base_dir / 'test_images'
            image_dir.mkdir()
            
            # Create required files
            (base_dir / 'CellPyAbility.cppipe').write_text('fake pipeline')
            cp_out = base_dir / 'cp_output'
            cp_out.mkdir()
            (cp_out / 'CellPyAbilityImage.csv').write_text('FileName_DAPI,Count_Nuclei\ntest.tif,100')
            
            # Mock __file__ to use temp directory
            with patch('cellpyability.toolbox.__file__', str(base_dir / 'toolbox.py')):
                # Call run_cellprofiler
                tb.run_cellprofiler(str(image_dir))
            
            # Verify subprocess.run was called
            self.assertTrue(mock_subprocess_run.called, "subprocess.run was not called")
            
            # Get the command that was passed to subprocess.run
            call_args = mock_subprocess_run.call_args
            command_list = call_args[0][0]
            
            # Print the command for visibility
            print(f"\nCellProfiler subprocess call verified")
            print(f"  Full command: {' '.join(str(a) for a in command_list)}")
            
            # Verify command structure
            self.assertEqual(len(command_list), 9,
                           f"Expected 9 arguments, got {len(command_list)}")
            
            # Verify executable
            self.assertEqual(command_list[0], '/usr/bin/cellprofiler',
                           "First argument should be CellProfiler executable")
            
            # Verify flags are in correct positions
            self.assertEqual(command_list[1], '-c', "Missing -c flag at position 1 (headless)")
            self.assertEqual(command_list[2], '-r', "Missing -r flag at position 2 (run)")
            self.assertEqual(command_list[3], '-p', "Missing -p flag at position 3 (pipeline)")
            self.assertEqual(command_list[5], '-i', "Missing -i flag at position 5 (input)")
            self.assertEqual(command_list[7], '-o', "Missing -o flag at position 7 (output)")
            
            # Verify paths are provided
            self.assertTrue(command_list[4], "Pipeline path should be at position 4")
            self.assertTrue(command_list[6], "Input directory should be at position 6")
            self.assertTrue(command_list[8], "Output directory should be at position 8")
            
            print(f"\n  Command breakdown:")
            print(f"    [0] Executable: {command_list[0]}")
            print(f"    [1] -c (headless mode)")
            print(f"    [2] -r (run pipeline)")
            print(f"    [3] -p (pipeline file flag)")
            print(f"    [4] Pipeline: {command_list[4]}")
            print(f"    [5] -i (input flag)")
            print(f"    [6] Input: {command_list[6]}")
            print(f"    [7] -o (output flag)")
            print(f"    [8] Output: {command_list[8]}")
            print(f"\n All required flags present in correct order")
    
    @patch('cellpyability.toolbox._ensure_cellprofiler_path')
    @patch('cellpyability.toolbox.subprocess.run')
    @patch('cellpyability.toolbox.pd.read_csv')
    @patch('cellpyability.toolbox.exit')  # Prevent exit() from terminating the test
    def test_cellprofiler_has_required_flags(self, mock_exit, mock_read_csv, mock_subprocess_run, mock_cp_path):
        """
        Test that all required CellProfiler flags are present.
        
        Required for headless execution: -c, -r, -p, -i, -o
        """
        # Setup mocks
        mock_cp_path.return_value = '/bin/cellprofiler'
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_read_csv.return_value = MagicMock()
        
        import cellpyability.toolbox as tb
        
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            img_dir = base_dir / 'imgs'
            img_dir.mkdir()
            
            (base_dir / 'CellPyAbility.cppipe').write_text('pipeline')
            out = base_dir / 'cp_output'
            out.mkdir()
            (out / 'CellPyAbilityImage.csv').write_text('data')
            
            with patch('cellpyability.toolbox.__file__', str(base_dir / 'toolbox.py')):
                tb.run_cellprofiler(str(img_dir))
            
            command = mock_subprocess_run.call_args[0][0]
            
            # Verify all required flags
            self.assertIn('-c', command, "Missing -c (headless)")
            self.assertIn('-r', command, "Missing -r (run)")
            self.assertIn('-p', command, "Missing -p (pipeline)")
            self.assertIn('-i', command, "Missing -i (input)")
            self.assertIn('-o', command, "Missing -o (output)")
            
            print(f"\n All CellProfiler flags verified: -c, -r, -p, -i, -o")


def main():
    """Run the tests."""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
