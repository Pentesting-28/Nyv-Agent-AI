import pytest
import os
from pathlib import Path
from src.tools.file_system import WriteFileTool, ReadFileTool

@pytest.mark.asyncio
async def test_write_and_read_file(tmp_path):
    # Use tmp_path which is usually under user home on local dev
    # If not, we might need to mock Path.home()
    
    test_file = tmp_path / "test_unit.txt"
    test_content = "Hello from unit tests"
    
    writer = WriteFileTool()
    reader = ReadFileTool()
    
    # Test Write
    write_result = await writer.execute(path=str(test_file), content=test_content)
    assert "Successfully wrote" in write_result
    assert test_file.exists()
    assert test_file.read_text(encoding='utf-8') == test_content
    
    # Test Read
    read_result = await reader.execute(path=str(test_file))
    assert test_content in read_result

@pytest.mark.asyncio
async def test_write_file_parameter_variants(tmp_path):
    test_file = tmp_path / "test_variants.txt"
    test_content = "Variant content"
    
    writer = WriteFileTool()
    
    # Test with 'file_path' instead of 'path'
    write_result = await writer.execute(file_path=str(test_file), content=test_content)
    assert "Successfully wrote" in write_result
    assert test_file.read_text(encoding='utf-8') == test_content

@pytest.mark.asyncio
async def test_read_nonexistent_file(tmp_path):
    reader = ReadFileTool()
    result = await reader.execute(path=str(tmp_path / "nonexistent.txt"))
    assert "Error: File" in result
    assert "does not exist" in result

@pytest.mark.asyncio
async def test_file_system_ops(tmp_path):
    from src.tools.file_system import ListDirectoryTool, MakeDirectoryTool, DeleteTool, MoveTool, CopyTool
    
    # 1. Make Directory
    mkdir_tool = MakeDirectoryTool()
    sub_dir = tmp_path / "subdir"
    await mkdir_tool.execute(path=str(sub_dir))
    assert sub_dir.is_dir()
    
    # 2. List Directory
    list_tool = ListDirectoryTool()
    (sub_dir / "file1.txt").write_text("content1")
    (sub_dir / "file2.py").write_text("content2")
    list_result = await list_tool.execute(path=str(sub_dir))
    assert "file1.txt" in list_result
    assert "file2.py" in list_result
    assert "[DIR]" not in list_result  # No subdirs inside subdir yet
    
    # 3. Copy Tool
    copy_tool = CopyTool()
    copy_dest = tmp_path / "file1_copy.txt"
    await copy_tool.execute(source=str(sub_dir / "file1.txt"), destination=str(copy_dest))
    assert copy_dest.exists()
    assert copy_dest.read_text() == "content1"
    
    # 4. Move Tool
    move_tool = MoveTool()
    move_dest = tmp_path / "moved_file.txt"
    await move_tool.execute(source=str(copy_dest), destination=str(move_dest))
    assert not copy_dest.exists()
    assert move_dest.exists()
    
    # 5. Delete Tool
    delete_tool = DeleteTool()
    await delete_tool.execute(path=str(move_dest))
    assert not move_dest.exists()

@pytest.mark.asyncio
async def test_file_system_advanced_ops(tmp_path):
    from src.tools.file_system import SearchFilesTool, AppendFileTool, BatchMoveTool, GetFileInfoTool
    
    # 1. Append File
    test_file = tmp_path / "append_test.txt"
    test_file.write_text("Part 1")
    append_tool = AppendFileTool()
    await append_tool.execute(path=str(test_file), content=" Part 2")
    assert test_file.read_text() == "Part 1 Part 2"
    
    # 2. Get File Info
    info_tool = GetFileInfoTool()
    info_result = await info_tool.execute(path=str(test_file))
    assert "Size:" in info_result
    assert "Type: File" in info_result
    
    # 3. Search Files
    search_tool = SearchFilesTool()
    (tmp_path / "script.py").write_text("print(1)")
    search_result = await search_tool.execute(pattern="*.py", path=str(tmp_path))
    assert "script.py" in search_result
    
    # 4. Batch Move
    batch_tool = BatchMoveTool()
    (tmp_path / "batch1.txt").write_text("1")
    (tmp_path / "batch2.txt").write_text("2")
    dest_dir = tmp_path / "batch_dest"
    dest_dir.mkdir()
    
    moves = [
        {"source": str(tmp_path / "batch1.txt"), "destination": str(dest_dir / "b1.txt")},
        {"source": str(tmp_path / "batch2.txt"), "destination": str(dest_dir / "b2.txt")}
    ]
    batch_result = await batch_tool.execute(moves=moves)
    assert "Successfully moved 2 items" in batch_result
    assert (dest_dir / "b1.txt").exists()
    assert (dest_dir / "b2.txt").exists()
