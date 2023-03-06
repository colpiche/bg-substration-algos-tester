from algo_tester.const import *
import os
from PIL import Image

class Comparator():
    def __init__(self, directory: str) -> None:
        self._directory: str = directory
        self._files: list[str] = os.listdir(directory)
        self._groundtruths: list[str] = []
        self._files_to_analyze: list[str] = []
        self._images_results: list[ImageResults] = []
        self._algos_stats: list[AlgoStats] = []
        self._datasets_stats: list[DatasetStats] = []
        self._init_lists()

    def _init_lists(self):
        for filename in self._files:
            file_details: list[str] = filename.split('_')

            if file_details[0] == "":
                continue
            elif file_details[0] == "GroundTruth":
                self._groundtruths.append(filename)
                continue
            elif file_details[0] in ALGORITHMS:
                self._files_to_analyze.append(filename)
            else:
                print(f'{filename} : filename not formatted as expected')

    def compare_images(self, ground_truth, processed_image) -> Results:
        if not (ground_truth.size == processed_image.size):
            print("Please provide 2 images with same size")
            return {
                "tn": 0,
                "tp": 0,
                "fn": 0,
                "fp": 0,
                "accuracy": 0
            }

        if not (ground_truth.mode == "L"):
            ground_truth = ground_truth.convert(mode="L")

        if not (processed_image.mode == "L"):
            processed_image = processed_image.convert(mode="L")

        ground_truth_list: list[int] = list(ground_truth.getdata())
        processed_image_list: list[int] = list(processed_image.getdata())

        tn: int = 0
        tp: int = 0
        fn: int = 0
        fp: int = 0

        for i in range(len(ground_truth_list)):
            if ground_truth_list[i] < 128 and processed_image_list[i] < 128:
                # True Negative
                tn += 1
            elif ground_truth_list[i] >= 128 and processed_image_list[i] >= 128:
                # True Positive
                tp += 1
            elif ground_truth_list[i] >= 128 and processed_image_list[i] < 128:
                # False Negative
                fn += 1
            elif ground_truth_list[i] < 128 and processed_image_list[i] >= 128:
                # False Positive
                fp += 1

        return {
            "tn": tn,
            "tp": tp,
            "fn": fn,
            "fp": fp,
            "accuracy": (tn + tp) / (tn + tp + fn + fp)
        }

    def compute_images_results(self):
        for filename in self._files_to_analyze:
            algo, dataset, *_ = filename.split('_')
            groundtruth_file: str = ""

            for value in self._groundtruths:
                if value.find(dataset) != -1:
                    groundtruth_file = value

            filepath: str = os.path.join(self._directory, filename)
            groundtruth_path: str = os.path.join(self._directory, groundtruth_file)

            processed_image = Image.open(filepath)
            groundtruth = Image.open(groundtruth_path)
            results: Results = self.compare_images(processed_image, groundtruth)

            self._images_results.append({
                "algo": algo,
                "dataset": dataset,
                "results": results
            })

        # ONLY FOR TESTING TO FIND THE BUG WHERE VALUES ARE SWITCHED BETWEEN DICTIONNARIES
        for result in self._images_results:
            if result["algo"] == "SigmaDelta" and result["dataset"] == "MovedObject":
                print(f'result from comparator: {result}')
                # print(f'fn = {result["results"]["fn"]}, fp = {result["results"]["fp"]}')
    
    def _compute_algos_stats(self):
        for algo in ALGORITHMS:
            pass