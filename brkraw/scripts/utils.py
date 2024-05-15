import click
from xnippet.formatter import StringFormatter as sf

def print_help_msg(ctx, param, value):
    if not value or not any(value):
        click.echo(ctx.get_help())
        ctx.exit()
        
def process_study_info(study, all=False):
    header = study.info()
    header_lines = []
    max_chars = sf.calc_max_char([k for k in header.keys()]) + 1
    for key, value in header.items():
        if key == "ParaVision":
            title = f"{key} {value}"
            header_lines.extend(["", title, '-'*len(title)])
            continue
        elif key == "AvailScanIDs":
            if all:
                continue
        elif key == "Weight":
            scale = 1000 if int(header['ParaVision'].split('.')[0]) > 5 else 1
            value = f"{value * scale:.2f} g"
        header_lines.append(f"{str(key).ljust(max_chars)}: {value}")
    return header_lines, max_chars
    
def prep_scan_info(study, scan_id, max_chars):
    scan_ids = scan_id if scan_id else study.avail
    if isinstance(scan_ids, int):
        scan_ids = [scan_ids]
    scans = study.info(scope='scans', scan_id=scan_ids)
    scanid_title = "[ScanID]".ljust(max_chars)
    scan_lines = [f"{scanid_title} Protocol :: Sequence :: [Parameters]"]
    scan_id_max = sf.calc_max_char([str(sid) for sid in scans.keys()])
    # print scans
    for scan_id, scan in scans.items():
        scan_lines.append(process_scan_info(scan_id, scan, scan_id_max))
        if 'recos' in scan.keys():
            scan_lines.extend(prep_reco_info(scan, scan_id_max))
    return scan_lines

def process_scan_info(scan_id, scan, scan_id_max):
    protocol_block = f"{scan['Protocol']} :: {scan['Sequence']} :: "
    scan_id_block = str(scan_id).zfill(scan_id_max)
    scan_line = []
    for k, v in scan.items():
        if k in ['Protocol', 'Sequence', 'recos']:
            continue
        if k in ["TR", 'TE']:
            if not isinstance(v, list):
                v = [v]
            v = ", ".join([f"{e:.2f}" for e in v]) + " ms"
        elif k == 'FlipAngle':
            v = f"{v} degree"
        elif k == "EffBW":
            v = f"{v:.2f} Hz"
        scan_line.append(f"{k}: {v}")
    if scan_line:
        scan_line = ", ".join(scan_line)
        scan_line = "\n" + " "*(5+scan_id_max) + f"[ {scan_line} ]"
    else:
        scan_line = ''
    return f"[{scan_id_block}]   {protocol_block}" + scan_line

def process_reco_info(reco_id_block, reco, indent):
    reco_contents = {0: []}
    counter = 0
    for k, v in reco.items():
        line_id = int(counter / 4)
        if line_id not in reco_contents.keys():
            reco_contents[line_id] = []
        if k == "MatrixSize":
            if not isinstance(v, list):
                v = [v]
            v = " x ".join([str(e) for e in v])
        elif k == "NumSlicePack":
            if v == 1:
                continue
        elif k == "NumSlices":
            if not isinstance(v, list):
                v = [v]
            v = ", ".join([f"{e}" for e in v])
        elif k == "Resolution":
            if not isinstance(v, list):
                v = [v]
            v = " x ".join([f"{e:.3f}" for e in v]) + " (mm)"
        elif k == "SliceDistances":
            if len(v) > 1:
                v = ", ".join([f"{e:.3f}" for e in v])
            elif len(v) == 1:
                v = v.pop()
            else:
                continue
            v = f"{v} (mm)"
        elif k == "dimDescription":
            v = " x ".join([e.capitalize() for e in v])
        elif k == "TemporalResol":
            v = f"{v / 1000:.2f} (s)"
        reco_contents[line_id].append(f"{k}: {v}")
        counter += 1
    reco_lines = []
    for lid, line in reco_contents.items():
        if lid == 0:
            reco_lines.append(reco_id_block + ', '.join(line))
        else:
            reco_lines.append(indent + ', '.join(line))
    return reco_lines


def prep_reco_info(scan, scan_id_max):
    # print recos
    recos = scan['recos']
    reco_blocks = []
    for reco_id, reco in recos.items():
        reco_id_block = " "*(scan_id_max + 1) + f"[{str(reco_id).zfill(2)}] "
        indent = " "*len(reco_id_block)
        reco_blocks.extend(process_reco_info(reco_id_block, reco, indent))
    return reco_blocks