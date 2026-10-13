import unittest
from unittest.mock import Mock, patch

from pqrsd.config import Config
from pqrsd.drive import DriveManager


class TestDriveManager(unittest.TestCase):
    def setUp(self):
        self.config = Mock(spec=Config)
        self.config.USE_GOOGLE_DRIVE = True
        self.config.GOOGLE_OAUTH_TOKEN = "fake_token.json"

    @patch("pqrsd.drive.DriveManager._get_drive_service")
    def test_buscar_archivo_exacto(self, mock_get_service):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_files = Mock()
        mock_service.files.return_value = mock_files
        mock_list_req = Mock()
        mock_files.list.return_value = mock_list_req
        mock_list_req.execute.return_value = {
            "files": [
                {
                    "id": "file123",
                    "name": "1. RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS.xlsx",
                }
            ]
        }

        dm = DriveManager(self.config)
        res = dm.buscar_archivo_por_nombre(
            "1. RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS.xlsx", "folder123"
        )
        self.assertIsNotNone(res)
        self.assertEqual(res["id"], "file123")
        self.assertEqual(
            res["name"], "1. RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS.xlsx"
        )
        mock_files.list.assert_called_once()

    @patch("pqrsd.drive.DriveManager._get_drive_service")
    def test_buscar_archivo_parcial(self, mock_get_service):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_files = Mock()
        mock_service.files.return_value = mock_files
        mock_list_req = Mock()
        mock_files.list.return_value = mock_list_req
        mock_list_req.execute.side_effect = [
            {"files": []},
            {
                "files": [
                    {
                        "id": "file456",
                        "name": "RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS",
                    }
                ]
            },
        ]

        dm = DriveManager(self.config)
        res = dm.buscar_archivo_por_nombre(
            "1. RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS.xlsx", "folder123"
        )
        self.assertIsNotNone(res)
        self.assertEqual(res["id"], "file456")
        self.assertEqual(res["name"], "RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS")
        self.assertEqual(mock_files.list.call_count, 2)

    @patch("pqrsd.drive.DriveManager._get_drive_service")
    def test_resolver_shortcut(self, mock_get_service):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_files = Mock()
        mock_service.files.return_value = mock_files
        mock_list_req = Mock()
        mock_files.list.return_value = mock_list_req
        mock_list_req.execute.return_value = {
            "files": [
                {
                    "id": "shortcut123",
                    "name": "RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS",
                    "mimeType": "application/vnd.google-apps.shortcut",
                    "shortcutDetails": {"targetId": "realfile789"},
                }
            ]
        }
        mock_get_req = Mock()
        mock_files.get.return_value = mock_get_req
        mock_get_req.execute.return_value = {
            "id": "realfile789",
            "name": "1. RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS.xlsx",
            "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }

        dm = DriveManager(self.config)
        res = dm.buscar_archivo_por_nombre(
            "1. RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS.xlsx", "folder123"
        )
        self.assertIsNotNone(res)
        self.assertEqual(res["id"], "realfile789")
        self.assertEqual(
            res["name"], "1. RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS.xlsx"
        )
        self.assertEqual(mock_files.list.call_count, 1)
        mock_files.get.assert_called_once_with(
            fileId="realfile789", fields="id, name, mimeType"
        )

    @patch("pqrsd.drive.DriveManager._get_drive_service")
    def test_shortcut_sin_target(self, mock_get_service):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_files = Mock()
        mock_service.files.return_value = mock_files
        mock_list_req = Mock()
        mock_files.list.return_value = mock_list_req
        mock_list_req.execute.return_value = {
            "files": [
                {
                    "id": "shortcut123",
                    "name": "RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS",
                    "mimeType": "application/vnd.google-apps.shortcut",
                    "shortcutDetails": {},
                }
            ]
        }

        dm = DriveManager(self.config)
        res = dm.buscar_archivo_por_nombre(
            "1. RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS.xlsx", "folder123"
        )
        self.assertIsNone(res)
        mock_files.list.assert_called_once()

    @patch("pqrsd.drive.DriveManager._get_drive_service")
    def test_archivo_no_encontrado(self, mock_get_service):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_files = Mock()
        mock_service.files.return_value = mock_files
        mock_list_req = Mock()
        mock_files.list.return_value = mock_list_req
        mock_list_req.execute.return_value = {"files": []}

        dm = DriveManager(self.config)
        res = dm.buscar_archivo_por_nombre(
            "1. RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS.xlsx", "folder123"
        )
        self.assertIsNone(res)


if __name__ == "__main__":
    unittest.main()
