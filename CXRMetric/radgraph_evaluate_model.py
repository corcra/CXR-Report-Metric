import json
import numpy as np
import os
import pandas as pd
from scipy import stats
from tqdm import tqdm

from CXRMetric.radgraph_inference import inference
#import radgraph_retrieve

"""Evalutes RadGraph results of reports generated by different models."""


np.random.seed(1357)

# RadGraph model path
radgraph_model_checkpoint = "/deep/group/radgraph/physionet.org/files/radgraph/1.0.0/models/model_checkpoint/model.tar.gz"

# TODO: scrub these paths
# Raw report paths
gt_oracle_raw_path = "/deep/u/fyu9/dygiepp/metric-oracles/gt_oracle_reports.csv"
bleu_oracle_raw_path = "/deep/u/fyu9/dygiepp/metric-oracles/bleu_oracle_reports.csv"
bleu_oracle_raw_path_2 = "/deep/u/rayank/CXR-RePaiR/bleu_hypothetical_bleu_eval.csv"
semb_oracle_raw_path = "/deep/u/fyu9/dygiepp/metric-oracles/semb_oracle_reports.csv"
semb_oracle_raw_path_2 = "/deep/u/rayank/CXR-RePaiR/semb_hypothetical_eval.csv"
bertscore_oracle_raw_path = "/deep/u/fyu9/dygiepp/metric-oracles/bertscore_oracle_reports.csv"
bertscore_oracle_raw_path_2 = "/deep/u/markendo/CXR-RePaiR/bertscore_best_matches/bertscore_mimic_study_level_retrieval.csv"
bertscore_oracle_raw_path_3 = "/deep/u/rayank/CXR-RePaiR/final/bertscore_copy.csv"
radgraph_oracle_raw_path = "/deep/u/fyu9/dygiepp/metric-oracles/radgraph_oracle_reports.csv"
wcl_raw_path = "/deep/u/fyu9/WCL/wcl_generated_reports.csv"
warmstart_raw_path = "/deep/u/fyu9/warm-start/generated_reports.csv"
random_raw_path = "/deep/u/fyu9/random/random_generated_reports.csv"

# RadGraph results paths
gt_path = "/deep/group/data/med-data/mimic-cxr-jpg-split/gt_oracle_radgraph.json"
bleu_path = "/deep/group/data/med-data/mimic-cxr-jpg-split/bleu_oracle_radgraph.json"
semb_path = "/deep/group/data/med-data/mimic-cxr-jpg-split/semb_oracle_radgraph.json"
bertscore_path = "/deep/group/data/med-data/mimic-cxr-jpg-split/bertscore_oracle_radgraph.json"
radgraph_path = "/deep/group/data/med-data/mimic-cxr-jpg-split/radgraph_oracle_radgraph.json"

ground_truth_path = "/deep/group/data/med-data/mimic-cxr-jpg-split/gt_radgraph.json"
m2trans_path = "/deep/group/data/med-data/mimic-cxr-jpg-split/m2trans_generated_radgraph.json"
r2gen_path = "/deep/group/data/med-data/mimic-cxr-jpg-split/r2gen_generated_radgraph.json"
clip_dir = "/deep/group/data/med-data/mimic-cxr-jpg-split/CXR-RePaiR-RadGraph/"
clip_files = [
        "clip_1_generated_radgraph.json",
        "clip_2_generated_radgraph.json",
        "clip_3_generated_radgraph.json",
        "clip_4_generated_radgraph.json",
        "clip_5_generated_radgraph.json",
        "clip_6_generated_radgraph.json",
        "clip_select_generated_radgraph.json",
]
wcl_path = "/deep/group/data/med-data/mimic-cxr-jpg-split/wcl_generated_radgraph.json"
warmstart_path = "/deep/group/data/med-data/mimic-cxr-jpg-split/warmstart_generated_radgraph.json"
random_path = "/deep/group/data/med-data/mimic-cxr-jpg-split/random_generated_radgraph.json"

bleu_entity_output_path = "/deep/u/fyu9/dygiepp/metric-oracles/bleu_radgraph_entity_f1.json"
bleu_relation_output_path = "/deep/u/fyu9/dygiepp/metric-oracles/bleu_radgraph_relation_f1.json"
semb_entity_output_path = "/deep/u/fyu9/dygiepp/metric-oracles/semb_radgraph_entity_f1.json"
semb_relation_output_path = "/deep/u/fyu9/dygiepp/metric-oracles/semb_radgraph_relation_f1.json"
bertscore_entity_output_path = "/deep/u/fyu9/dygiepp/metric-oracles/bertscore_radgraph_entity_f1.json"
bertscore_relation_output_path = "/deep/u/fyu9/dygiepp/metric-oracles/bertscore_radgraph_relation_f1.json"
radgraph_entity_output_path = "/deep/u/fyu9/dygiepp/metric-oracles/radgraph_radgraph_entity_f1.json"
radgraph_relation_output_path = "/deep/u/fyu9/dygiepp/metric-oracles/radgraph_radgraph_relation_f1.json"

m2trans_entity_output_path = "/deep/u/fyu9/dygiepp/m2trans_radgraph_entity_f1.json"
m2trans_relation_output_path = "/deep/u/fyu9/dygiepp/m2trans_radgraph_relation_f1.json"
r2gen_entity_output_path = "/deep/u/fyu9/dygiepp/r2gen_radgraph_entity_f1.json"
r2gen_relation_output_path = "/deep/u/fyu9/dygiepp/r2gen_radgraph_relation_f1.json"
clip_output_dir = "/deep/u/fyu9/dygiepp/CXR-RePaiR-RadGraph/"
clip_entity_output_files = [
        "clip_1_radgraph_entity_f1.json",
        "clip_2_radgraph_entity_f1.json",
        "clip_3_radgraph_entity_f1.json",
        "clip_4_radgraph_entity_f1.json",
        "clip_5_radgraph_entity_f1.json",
        "clip_6_radgraph_entity_f1.json",
        "clip_select_radgraph_entity_f1.json",
]
clip_relation_output_files = [
        "clip_1_radgraph_relation_f1.json",
        "clip_2_radgraph_relation_f1.json",
        "clip_3_radgraph_relation_f1.json",
        "clip_4_radgraph_relation_f1.json",
        "clip_5_radgraph_relation_f1.json",
        "clip_6_radgraph_relation_f1.json",
        "clip_select_radgraph_relation_f1.json",
]
wcl_entity_output_path = "/deep/u/fyu9/dygiepp/wcl_radgraph_entity_f1.json"
wcl_relation_output_path = "/deep/u/fyu9/dygiepp/wcl_radgraph_relation_f1.json"
warmstart_entity_output_path = "/deep/u/fyu9/dygiepp/warmstart_radgraph_entity_f1.json"
warmstart_relation_output_path = "/deep/u/fyu9/dygiepp/warmstart_radgraph_relation_f1.json"
random_entity_output_path = "/deep/u/fyu9/dygiepp/random_radgraph_entity_f1.json"
random_relation_output_path = "/deep/u/fyu9/dygiepp/random_radgraph_relation_f1.json"

def compute_f1(test, retrieved):
    """Computes F1 between test/retrieved report's entities or relations.

    Args:
      test: Set of test report's entities or relations.
      retrieved: Set of potential retrieved report's entities or relations.

    Returns:
      Entity or relation match F1 score.
    """
    true_positives = len(test.intersection(retrieved))
    false_positives = len(retrieved) - true_positives
    false_negatives = len(test) - true_positives
    precision = true_positives / (true_positives + false_positives) \
            if true_positives + false_positives != 0 else 0
    recall = true_positives / (true_positives + false_negatives) \
            if true_positives + false_negatives != 0 else 0
    f1 = 2 * precision * recall / (precision + recall) \
            if precision + recall != 0 else 0
    return f1

def generate_radgraph(model_path, raw_path, output_path, cuda=0,
                      start=None, end=None,
                      sentence=False, image=False,
                      data_source="MIMIC-CXR", data_split="metric-oracle"):
    """Generates RadGraph entities and relations from reports.

    Assumes that the CSV at `raw_path` has a "report" column with reports and
    a "study_id" column (along with a "sentence_id" column if `sentence` is
    True and a "dicom_id" column if `image` is True).

    Code adapted from
        https://physionet.org/content/radgraph/1.0.0: models/inference.py.
    Requires dependencies and dygie/ from
        https://github.com/dwadden/dygiepp.git.
    Requires model checkpoint.

    Args:
      model_path: Path to RadGraph model checkpoint.
      raw_path: Path to CSV of reports.
      output_path: Path to output JSON RadGraph entities and relations.
      start: Start of range of reports to compute.
      end: End of range of reports to compute (exclusive).
      cuda: ID of GPU device.
      data_source: Tag of data source.
      data_split: Tag of data split.
      sentence: Whether to generate RadGraph objects for individual sentences,
          which are distinguished by study_id and sentence_id.
      image: Whether to generate RadGraph objects for individual DICOM images,
          which are distinguished by dicom_id.
    """
    print("Preprocessing all the reports...")
    inference.preprocess_reports(
            raw_path, start, end, sentence=sentence, image=image)
    print("Done with preprocessing.")

    print("Running the inference now... This can take a bit of time")
    inference.run_inference(model_path, cuda)
    print("Inference completed.")

    print("Postprocessing output file...")
    final_dict = inference.postprocess_reports(data_source, data_split)
    print("Done postprocessing.")

    print("Saving results and performing final cleanup...")
    inference.cleanup()

    with open(output_path, "w") as outfile:
        json.dump(final_dict, outfile)


def parse_entity_relation(path):
    """Parses entities and relations from RadGraph outputs.

    Args:
      path: Path to RadGraph outputs.

    Returns:
      Entities as {(token, label), ...}, and relations as
      {(entity1, entity2, relation), ...}.
    """
    with open(path, "r") as f:
        radgraph_results = json.load(f)

    entities = {dicom_report_id: {(entity["tokens"], entity["label"]) \
                            for _, entity in outputs["entities"].items()} \
                for (dicom_report_id, outputs) in tqdm(radgraph_results.items())}

    relations = dict()
    for dicom_report_id, outputs in tqdm(radgraph_results.items()):
        relations[dicom_report_id] = set()
        for _, entity in outputs["entities"].items():
            relations[dicom_report_id].update(
                    {((entity["tokens"], entity["label"]),
                      (radgraph_results[dicom_report_id]["entities"]\
                               [relation[1]]["tokens"],
                       radgraph_results[dicom_report_id]["entities"]\
                               [relation[1]]["label"]),
                      relation[0],
                     ) for relation in entity["relations"]})

    return entities, relations


def evaluate_radgraph(ground_truth_path, generated_path,
                      entity_output_path, relation_output_path):
    """Evaluates RadGraph entities and relations overlap in F1 scores.

    Note that for a study with multiple images (DICOM IDs), we take the report
    of some image with the highest RadGraph F1 score.

    Args:
      ground_truth_path: Path to ground-truth reports RadGraph outputs.
      generated_path: Path to generated reports RadGraph outputs.
      entity_output_path: Path to write entity F1 scores as
          {study ID: (F1, DICOM ID, (test entity count, generated entity
                                     count))}.
      relation_output_path: Path to write relation F1 scores as
          {study ID: (F1, DICOM ID, (test relation count, generated relation
                                     count))}.
    """
    ground_truth_entities, ground_truth_relations = \
            parse_entity_relation(ground_truth_path)
    generated_entities, generated_relations = \
            parse_entity_relation(generated_path)

    entity_f1s = {}
    relation_f1s = {}
    for dicom_report_id, results in ground_truth_entities.items():
        if not dicom_report_id in generated_entities:  # 0 match
            generated_entities[dicom_report_id] = {}
        f1 = compute_f1(
                results,
                generated_entities[dicom_report_id])
        try:
            dicom_id, report_id = dicom_report_id.split("_")
        except ValueError:
            dicom_id = None
            report_id = dicom_report_id
        if not report_id in entity_f1s:
            entity_f1s[report_id] = \
                    (f1, dicom_id, (len(results),
                                    len(generated_entities[dicom_report_id])))
        elif f1 > entity_f1s[report_id][0]:
            entity_f1s[report_id] = \
                    (f1, dicom_id, (len(results),
                                    len(generated_entities[dicom_report_id])))
    for dicom_report_id, results in ground_truth_relations.items():
        if not dicom_report_id in generated_relations:  # 0 match
            generated_relations[dicom_report_id] = {}
        f1 = compute_f1(
                results,
                generated_relations[dicom_report_id])
        try:
            dicom_id, report_id = dicom_report_id.split("_")
        except ValueError:
            dicom_id = None
            report_id = dicom_report_id
        if not report_id in relation_f1s:
            relation_f1s[report_id] = \
                    (f1, dicom_id, (len(results),
                                    len(generated_relations[dicom_report_id])))
        elif f1 > relation_f1s[report_id][0]:
            relation_f1s[report_id] = \
                    (f1, dicom_id, (len(results),
                                    len(generated_relations[dicom_report_id])))

    with open(entity_output_path, "w") as f:
        json.dump(entity_f1s, f)
    with open(relation_output_path, "w") as f:
        json.dump(relation_f1s, f)

    # Average over all reports (study ID level)
    avg_entity_f1 = sum(
            [f1 for f1, _, _ in entity_f1s.values()]) / len(entity_f1s)
    avg_relation_f1 = sum(
            [f1 for f1, _, _ in relation_f1s.values()]) / len(relation_f1s)
    print(f"Average RadGraph entity F1 = {avg_entity_f1}\n"
          f"Average RadGraph relation F1 = {avg_relation_f1}\n")

    # Compute average entity and relation counts over reports (study ID level)
    gt_entity_count = sum(
            [gt_count for f1, _, (gt_count, _) \
             in entity_f1s.values()]) / len(entity_f1s)
    gt_relation_count = sum(
            [gt_count for f1, _, (gt_count, _) \
             in relation_f1s.values()]) / len(relation_f1s)
    avg_entity_count = sum(
            [generated_count for f1, _, (_, generated_count) \
             in entity_f1s.values()]) / len(entity_f1s)
    avg_relation_count = sum(
            [generated_count for f1, _, (_, generated_count) \
             in relation_f1s.values()]) / len(relation_f1s)
    print(f"Ground truth average RadGraph entity counts = {gt_entity_count}\n"
          f"Ground truth average RadGraph relation counts = {gt_relation_count}\n"
          f"Average RadGraph entity counts = {avg_entity_count}\n"
          f"Average RadGraph relation counts = {avg_relation_count}\n")

    print(f"#Test reports (this is all test cases): {len(entity_f1s)}")


def add_radgraph_results_to_csv(entity_output_path, relation_output_path,
                                csv_path):
    """Adds RadGraph scores as columns to CSV indexed by study_id.

    RadGraph scores are added as "radgraph_entity", "radgraph_relation",
    "radgraph_combined".

    Args:
      entity_output_path: Path to json of entity F1 scores as
          {study ID: (F1, DICOM ID, (test entity count, generated entity
                                     count))}.
      relation_output_path: Path to json of relation F1 scores as
          {study ID: (F1, DICOM ID, (test relation count, generated relation
                                     count))}.
      csv_path: Path to CSV indexed by study_id.
    """
    with open(entity_output_path, "r") as f:
        entity_f1s = json.load(f)
    with open(relation_output_path, "r") as f:
        relation_f1s = json.load(f)
    df = pd.read_csv(csv_path)
    entity_results = []
    relation_results = []
    combined_results = []
    for index, row in df.iterrows():
        study_id = str(row["study_id"])
        entity_f1, _, _ = entity_f1s[study_id]
        relation_f1, _, _ = relation_f1s[study_id]
        entity_results.append(entity_f1)
        relation_results.append(relation_f1)
        combined_results.append((entity_f1 + relation_f1) / 2)
    df["radgraph_entity"] = entity_results
    df["radgraph_relation"] = relation_results
    df["radgraph_combined"] = combined_results
    df.to_csv(csv_path)


def compute_CI(entity_output_path, relation_output_path, bootstrap_k=5000,
               level=0.95):
    """Adds RadGraph scores as columns to CSV indexed by study_id.

    RadGraph scores are added as "radgraph_entity", "radgraph_relation",
    "radgraph_combined".

    Args:
      entity_output_path: Path to json of entity F1 scores as
          {study ID: (F1, DICOM ID, (test entity count, generated entity
                                     count))}.
      relation_output_path: Path to json of relation F1 scores as
          {study ID: (F1, DICOM ID, (test relation count, generated relation
                                     count))}.
      csv_path: Path to CSV indexed by study_id.
    """
    def _compute_CI(output_path, output_type, bootstrap_k, level):
        print("\nComputing confidence intervals (CIs)...")
        with open(output_path, "r") as f:
            f1s = json.load(f)
        print(f"{output_type} result #study_ids: {len(f1s)}")
        results = [f1 for f1, _, _ in f1s.values()]

        results = np.array(results)
        bootstrap = np.random.choice(results, size=bootstrap_k, replace=True)
        mean, ste = np.mean(bootstrap), stats.sem(bootstrap)
        ci  = ste * stats.t.ppf((1 + level) / 2., len(bootstrap) - 1)
        print(f"CI: [{mean - ci:.3f}, {mean:.3f}, {mean + ci:.3f}]")
    _compute_CI(entity_output_path, "Entity", bootstrap_k=bootstrap_k,
                level=level)
    _compute_CI(relation_output_path, "Relation", bootstrap_k=bootstrap_k,
                level=level)


"""
takes two paths to csvs with column "report"
"""
def run_radgraph(gt_path, pred_path, out_dir):
    """ run for gt and reports to generate
    input: checkpoint, csv of reports (text), output path
    return:
    entity + relation json files??
    """
    gt_out_path = os.path.join(out_dir,"gt_cache.json")
    pred_out_path = os.path.join(out_dir,"pred_cache.json")
    out_entities = os.path.join(out_dir,"entities_cache.json")
    out_relations = os.path.join(out_dir,"relations_cache.json")

    # get entities and relations for ground truth
    generate_radgraph(radgraph_model_checkpoint, gt_path, gt_out_path)
    generate_radgraph(radgraph_model_checkpoint, pred_path, pred_out_path)

    # get entities and relations for predicted BASED on ground truth
    evaluate_radgraph(gt_out_path, pred_out_path,
                      out_entities, out_relations)

    return (out_entities, out_relations)


