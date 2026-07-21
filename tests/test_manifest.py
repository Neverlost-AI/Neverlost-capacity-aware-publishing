import importlib.util
import copy
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_short", ROOT / "build_short.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class GovernedManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((ROOT / "manifests/patients_paradox_short.json").read_text(encoding="utf-8"))

    def test_source_and_timing_gate(self):
        report = MODULE.validate(self.manifest)
        self.assertEqual(report["status"], "VALIDATED_FOR_REVIEW_BUILD")
        self.assertAlmostEqual(report["audio_duration"], 36.93, places=2)

    def test_release_status_is_review_only(self):
        self.assertEqual(self.manifest["status"], "REVIEW_ONLY")

    def test_all_narration_is_source_bound(self):
        approved = " ".join((ROOT / self.manifest["source"]["path"]).read_text(encoding="utf-8").split())
        for segment in self.manifest["audio_segments"]:
            self.assertIn(" ".join(segment["source_text"].split()), approved)

    def assert_blocked(self, manifest, message):
        with self.assertRaises(SystemExit) as context:
            MODULE.validate(manifest)
        self.assertIn(message, str(context.exception))

    def test_changed_source_hash_is_blocked(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["source"]["sha256"] = "0" * 64
        self.assert_blocked(manifest, "approved source hash changed")

    def test_changed_audio_hash_is_blocked(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["audio_segments"][0]["sha256"] = "0" * 64
        self.assert_blocked(manifest, "controlled audio hash changed")

    def test_changed_logo_hash_is_blocked(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["brand"]["logo_sha256"] = "0" * 64
        self.assert_blocked(manifest, "controlled logo hash changed")

    def test_unapproved_narration_is_blocked(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["audio_segments"][0]["source_text"] = "This language is not in the approved source."
        self.assert_blocked(manifest, "narration is not verbatim approved source")

    def test_automated_approval_is_blocked(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["status"] = "APPROVED"
        self.assert_blocked(manifest, "automated build may only produce REVIEW_ONLY")

    def test_scene_timing_mismatch_is_blocked(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["scenes"][0]["duration"] += 1
        self.assert_blocked(manifest, "does not match audio")

    def test_caption_overlap_is_blocked(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["captions"][1]["start"] = 3.0
        self.assert_blocked(manifest, "overlaps the previous cue")

    def test_unbound_caption_text_is_blocked(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["captions"][0]["text"] = "A generated claim absent from narration."
        self.assert_blocked(manifest, "not bound to declared narration")

    def test_path_escape_is_blocked(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["audio_segments"][0]["path"] = "../../outside.wav"
        self.assert_blocked(manifest, "path escapes project root")

    def test_missing_caption_set_is_blocked(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["captions"] = []
        self.assert_blocked(manifest, "at least one caption cue is required")

    def test_recovery_profile_defers_release_work(self):
        plan = MODULE.capacity_plan(self.manifest, "recovery", 8.0, {"start_build", "render_media", "build_captions", "build_qa"})
        self.assertEqual(plan["status"], "REVIEW_ONLY_CHECKPOINT_SAVED")
        self.assertLessEqual(plan["active_minutes_used_or_scheduled"], 8.0)
        self.assertEqual(plan["next_task"]["id"], "metadata")

    def test_distinct_synthetic_case_validates(self):
        path = ROOT / "manifests/recovery_aware_synthetic_demo.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        report = MODULE.validate(manifest, path)
        self.assertEqual(report["status"], "VALIDATED_FOR_REVIEW_BUILD")
        self.assertAlmostEqual(report["audio_duration"], 36.15, places=2)
        self.assertNotIn("logo", manifest["brand"])


if __name__ == "__main__":
    unittest.main()
