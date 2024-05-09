from flask import Flask, request, jsonify, render_template
import caveclient
import pandas as pd
import numpy as np
import json

app = Flask(__name__)

# Initialize CAVE client globally if no initial configuration is needed
# or move this inside the relevant functions if configurations are dynamic based on the request
client = caveclient.CAVEclient()

available_datastacks = [
    'minnie35_public_v0', 'minnie65_phase3_v0', 'fanc_sandbox',
    'minnie65_public_v117', 'minnie65_public_v343', 'flywire_fafb_sandbox',
    'minnie65_phase2_flat', 'minnie65_public', 'minnie35_phase3_v0',
    'basil-seg-aug', 'minnie65_phase3_v1', 'minnie65_public_v661',
    'pinky_sandbox', 'fafb_v15_20221128025036', 'flywire_fafb_public', 'minnie65_sandbox'
]

def make_tag_entry(taglists, tagdescription_ds, description="tags"):
    unique_tag_lists = [np.unique(tl).tolist() for tl in taglists]
    unique_tags = np.concatenate(unique_tag_lists).tolist()
    unique_tag_descs = [[tag_d[t] for t in tl] for tl, tag_d in zip(unique_tag_lists, tagdescription_ds)]
    unique_tag_desc = np.concatenate(unique_tag_descs).tolist()
    tag_indices = [[unique_tags.index(t) for t in tl] for tl in taglists]
    tag_indices = [list(tags) for tags in zip(*tag_indices)]
    return {
        "id": "tags",
        "type": "tags",
        "description": description,
        "tags": unique_tags,
        "tag_descriptions": unique_tag_desc,
        "values": tag_indices
    }

@app.route('/')
def index():
    return render_template('frontend.html', datastacks=available_datastacks)

@app.route('/initialize_client', methods=['POST'])
def initialize_client():
    dataset_id = request.form.get('datasetId')
    response = {"message": "Client initialized with dataset ID: {}".format(dataset_id)}
    return jsonify(response)

@app.route('/fetch_tables', methods=['POST'])
def fetch_tables():
    selected_datastack = request.form['datastack']
    local_client = caveclient.CAVEclient(datastack_name=selected_datastack)
    all_tables = local_client.annotation.get_tables()
    tables_data = [{'label': table, 'value': table} for table in all_tables]
    return jsonify({'tables': tables_data})

@app.route('/generate_url', methods=['POST'])
def generate_url():
    try:
        datastack = request.form.get('datastack')
        table = request.form.get('table')
        local_client = caveclient.CAVEclient(datastack)
        ct_df = local_client.materialize.query_table(table)

        unique_ct = ct_df.cell_type.unique()
        unique_class = ct_df.classification_system.unique()

        ct_desc = {c: c for c in unique_ct}
        ct_desc.update({
            'PTC': 'Proximal targeting interneuron',
            'DTC': "Distal targeting interneuron",
            'ITC': "Interneuron targeting interneuron",
            'STC': "Sparsely targeting interneuron",
            'L5NP': "Layer 5 Near Projecting"
        })

        cell_class_desc = {c: c for c in unique_class}

        tag_entry = make_tag_entry([ct_df.cell_type, ct_df.classification_system],
                                   [ct_desc, cell_class_desc])

        segment_info = {
            "@type": "neuroglancer_segment_properties",
            "inline": {
                "ids": [str(i) for i in ct_df.pt_root_id.values.tolist()],
                "properties": [
                    {"id": "label", "type": "label", "description": "filename", "values": [str(v) for v in ct_df.pt_root_id.values]},
                    tag_entry,
                ]
            }
        }

        segment_id = local_client.state.upload_property_json(segment_info)
        # Adjusting the call here to match the available parameters
        ngl_url = f"precomputed://middleauth+https://global.daf-apis.com/nglstate/api/v1/property/{segment_id}"
        return jsonify({'url': ngl_url})


    except Exception as e:
        app.logger.error(f"Error generating URL: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
