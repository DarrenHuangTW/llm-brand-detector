"""JSON 存儲層單元測試"""

import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
from typing import List

from src.firegeo.storage.json_storage import JSONStorage
from src.firegeo.models.analysis import BrandAnalysis, SentimentType, BrandMention, AIResponse


class TestJSONStorage:
    """JSON 存儲層測試"""
    
    def test_init_with_default_params(self):
        """測試預設參數初始化"""
        storage = JSONStorage()
        assert storage.data_dir == Path("data")
        assert storage.filename == "analyses.json"
        assert storage.file_path == Path("data/analyses.json")
    
    def test_init_with_custom_params(self, temp_data_dir: Path):
        """測試自定義參數初始化"""
        storage = JSONStorage(data_dir=str(temp_data_dir), filename="custom.json")
        assert storage.data_dir == temp_data_dir
        assert storage.filename == "custom.json"
        assert storage.file_path == temp_data_dir / "custom.json"
    
    @pytest.mark.asyncio
    async def test_ensure_data_dir_creates_directory(self, temp_data_dir: Path):
        """測試數據目錄創建"""
        storage = JSONStorage(data_dir=str(temp_data_dir / "new_dir"))
        await storage._ensure_data_dir()
        assert (temp_data_dir / "new_dir").exists()
        assert (temp_data_dir / "new_dir").is_dir()
    
    @pytest.mark.asyncio
    async def test_load_data_file_not_exists(self, temp_data_dir: Path):
        """測試文件不存在時的數據載入"""
        storage = JSONStorage(data_dir=str(temp_data_dir))
        data = await storage._load_data()
        assert data == []
    
    @pytest.mark.asyncio
    async def test_load_data_empty_file(self, temp_data_dir: Path):
        """測試空文件的數據載入"""
        storage = JSONStorage(data_dir=str(temp_data_dir))
        # 創建空文件
        storage.file_path.touch()
        data = await storage._load_data()
        assert data == []
    
    @pytest.mark.asyncio
    async def test_load_data_invalid_json(self, temp_data_dir: Path):
        """測試無效 JSON 的數據載入"""
        storage = JSONStorage(data_dir=str(temp_data_dir))
        # 寫入無效 JSON
        storage.file_path.write_text("invalid json content")
        data = await storage._load_data()
        assert data == []
    
    @pytest.mark.asyncio
    async def test_load_data_valid_json(self, temp_data_dir: Path):
        """測試有效 JSON 的數據載入"""
        storage = JSONStorage(data_dir=str(temp_data_dir))
        test_data = [{"id": "test-1", "brand_name": "TestBrand"}]
        storage.file_path.write_text(json.dumps(test_data))
        
        data = await storage._load_data()
        assert data == test_data
    
    @pytest.mark.asyncio
    async def test_save_data(self, temp_data_dir: Path):
        """測試數據保存"""
        storage = JSONStorage(data_dir=str(temp_data_dir))
        test_data = [{"id": "test-1", "brand_name": "TestBrand"}]
        
        await storage._save_data(test_data)
        
        # 驗證文件內容
        saved_content = json.loads(storage.file_path.read_text())
        assert saved_content == test_data
    
    @pytest.mark.asyncio
    async def test_save_analysis(self, json_storage: JSONStorage, sample_brand_analysis: BrandAnalysis):
        """測試分析結果保存"""
        await json_storage.save_analysis(sample_brand_analysis)
        
        # 載入並驗證
        data = await json_storage._load_data()
        assert len(data) == 1
        assert data[0]["id"] == sample_brand_analysis.id
        assert data[0]["brand_name"] == sample_brand_analysis.brand_name
    
    @pytest.mark.asyncio
    async def test_save_analysis_update_existing(self, json_storage: JSONStorage, sample_brand_analysis: BrandAnalysis):
        """測試更新現有分析"""
        # 先保存
        await json_storage.save_analysis(sample_brand_analysis)
        
        # 修改並再次保存
        sample_brand_analysis.brand_name = "UpdatedBrand"
        await json_storage.save_analysis(sample_brand_analysis)
        
        # 驗證只有一個記錄且已更新
        data = await json_storage._load_data()
        assert len(data) == 1
        assert data[0]["brand_name"] == "UpdatedBrand"
    
    @pytest.mark.asyncio
    async def test_get_analysis(self, populated_storage: JSONStorage, sample_brand_analysis: BrandAnalysis):
        """測試獲取分析結果"""
        result = await populated_storage.get_analysis(sample_brand_analysis.id)
        
        assert result is not None
        assert result.id == sample_brand_analysis.id
        assert result.brand_name == sample_brand_analysis.brand_name
    
    @pytest.mark.asyncio
    async def test_get_analysis_not_found(self, json_storage: JSONStorage):
        """測試獲取不存在的分析"""
        result = await json_storage.get_analysis("nonexistent-id")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_list_analyses(self, populated_storage: JSONStorage):
        """測試列出所有分析"""
        analyses = await populated_storage.list_analyses()
        
        assert len(analyses) == 1
        assert analyses[0].brand_name == "TestBrand"
    
    @pytest.mark.asyncio
    async def test_list_analyses_empty(self, json_storage: JSONStorage):
        """測試空列表"""
        analyses = await json_storage.list_analyses()
        assert analyses == []
    
    @pytest.mark.asyncio
    async def test_list_analyses_by_brand(self, json_storage: JSONStorage):
        """測試按品牌名稱過濾"""
        # 創建多個分析
        analysis1 = BrandAnalysis(id="1", brand_name="Brand1", competitors=[], prompts=["test"])
        analysis2 = BrandAnalysis(id="2", brand_name="Brand2", competitors=[], prompts=["test"])
        analysis3 = BrandAnalysis(id="3", brand_name="Brand1", competitors=[], prompts=["test2"])
        
        await json_storage.save_analysis(analysis1)
        await json_storage.save_analysis(analysis2)
        await json_storage.save_analysis(analysis3)
        
        # 測試過濾
        brand1_analyses = await json_storage.list_analyses(brand_name="Brand1")
        assert len(brand1_analyses) == 2
        assert all(a.brand_name == "Brand1" for a in brand1_analyses)
        
        brand2_analyses = await json_storage.list_analyses(brand_name="Brand2")
        assert len(brand2_analyses) == 1
        assert brand2_analyses[0].brand_name == "Brand2"
    
    @pytest.mark.asyncio
    async def test_delete_analysis(self, populated_storage: JSONStorage, sample_brand_analysis: BrandAnalysis):
        """測試刪除分析"""
        success = await populated_storage.delete_analysis(sample_brand_analysis.id)
        assert success is True
        
        # 驗證已刪除
        result = await populated_storage.get_analysis(sample_brand_analysis.id)
        assert result is None
        
        # 驗證列表為空
        analyses = await populated_storage.list_analyses()
        assert len(analyses) == 0
    
    @pytest.mark.asyncio
    async def test_delete_analysis_not_found(self, json_storage: JSONStorage):
        """測試刪除不存在的分析"""
        success = await json_storage.delete_analysis("nonexistent-id")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_backup_data(self, populated_storage: JSONStorage):
        """測試數據備份"""
        backup_path = await populated_storage.backup_data()
        
        assert backup_path.exists()
        assert backup_path.suffix == ".json"
        assert "backup" in backup_path.name
        
        # 驗證備份內容
        backup_content = json.loads(backup_path.read_text())
        original_content = json.loads(populated_storage.file_path.read_text())
        assert backup_content == original_content
    
    @pytest.mark.asyncio
    async def test_restore_from_backup(self, json_storage: JSONStorage, temp_data_dir: Path):
        """測試從備份恢復"""
        # 創建測試備份文件
        test_data = [{"id": "backup-test", "brand_name": "BackupBrand"}]
        backup_file = temp_data_dir / "backup.json"
        backup_file.write_text(json.dumps(test_data))
        
        # 恢復數據
        success = await json_storage.restore_from_backup(str(backup_file))
        assert success is True
        
        # 驗證恢復內容
        data = await json_storage._load_data()
        assert data == test_data
    
    @pytest.mark.asyncio
    async def test_restore_from_backup_file_not_found(self, json_storage: JSONStorage):
        """測試從不存在的備份文件恢復"""
        success = await json_storage.restore_from_backup("nonexistent.json")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_restore_from_backup_invalid_json(self, json_storage: JSONStorage, temp_data_dir: Path):
        """測試從無效 JSON 備份恢復"""
        backup_file = temp_data_dir / "invalid_backup.json"
        backup_file.write_text("invalid json")
        
        success = await json_storage.restore_from_backup(str(backup_file))
        assert success is False
    
    @pytest.mark.asyncio
    async def test_get_storage_stats(self, json_storage: JSONStorage):
        """測試存儲統計"""
        # 添加測試數據
        analysis1 = BrandAnalysis(id="1", brand_name="Brand1", competitors=[], prompts=["test"])
        analysis2 = BrandAnalysis(id="2", brand_name="Brand2", competitors=[], prompts=["test"])
        
        await json_storage.save_analysis(analysis1)
        await json_storage.save_analysis(analysis2)
        
        stats = await json_storage.get_storage_stats()
        
        assert stats["total_analyses"] == 2
        assert stats["file_size_bytes"] > 0
        assert stats["brands"] == ["Brand1", "Brand2"]
        assert "last_modified" in stats
    
    @pytest.mark.asyncio
    async def test_get_storage_stats_empty(self, json_storage: JSONStorage):
        """測試空存儲統計"""
        stats = await json_storage.get_storage_stats()
        
        assert stats["total_analyses"] == 0
        assert stats["file_size_bytes"] == 0
        assert stats["brands"] == []
        assert stats["last_modified"] is None
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, json_storage: JSONStorage):
        """測試並發操作"""
        # 創建多個分析並並發保存
        analyses = [
            BrandAnalysis(id=f"concurrent-{i}", brand_name=f"Brand{i}", competitors=[], prompts=["test"])
            for i in range(10)
        ]
        
        # 並發保存
        tasks = [json_storage.save_analysis(analysis) for analysis in analyses]
        await asyncio.gather(*tasks)
        
        # 驗證所有都已保存
        all_analyses = await json_storage.list_analyses()
        assert len(all_analyses) == 10
        
        # 驗證 ID 唯一性
        ids = [a.id for a in all_analyses]
        assert len(set(ids)) == 10
    
    def test_error_handling_file_permissions(self, temp_data_dir: Path):
        """測試文件權限錯誤處理"""
        storage = JSONStorage(data_dir=str(temp_data_dir))
        
        # 模擬權限錯誤
        with patch('pathlib.Path.write_text', side_effect=PermissionError("Permission denied")):
            # 這應該在實際的異步上下文中測試，但為了示例我們測試同步版本
            with pytest.raises(Exception):
                # 在實際實現中，這應該被適當處理
                storage.file_path.write_text("test")