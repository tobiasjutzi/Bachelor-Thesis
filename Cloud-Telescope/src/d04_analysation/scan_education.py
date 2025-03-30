import pandas as pd
from src.d04_analysation.count_percent import *
from dataclasses import dataclass
import datetime

@dataclass
class Education:
    uni_name: str
    rir_name: str
    total_ip: int
    ports: list[str]
    dns_value: list[str]
    country: str

@dataclass
class EducationList:
    uni_list: list[Education]


de_educations: EducationList = EducationList(
    uni_list=[
        Education(
            uni_name='Ruhr-Universitaet Bochum',
            rir_name='Ruhr-Universitaet Bochum',
            total_ip=1,
            ports=['5683', '5684', '53'],
            dns_value=['ports-measurements.softsec.ruhr-uni-bochum.de'],
            country='DE'
        ),
        Education(
            uni_name='HAW Hamburg',
            rir_name='Verein zur Foerderung eines Deutschen Forschungsnetzes e.V.',
            total_ip=1,
            ports=['53'],
            dns_value=['research-scan1.inet.haw-hamburg.de'],
            country='DE'
                ),
        Education(
            uni_name='Max-Planck-Institut für Informatik',
            rir_name='Verein zur Foerderung eines Deutschen Forschungsnetzes e.V.',
            total_ip=1,
            ports=['123'],
            dns_value=['inet-research-scan-1.mpi-inf.mpg.de'],
            country='DE'
                ),
        Education(
            uni_name='RWTH Aachen',
            rir_name='RWTH Aachen University',
            total_ip=2,
            ports=['53', '443'],
            dns_value=['researchscan27.comsys.rwth-aachen.de', 'researchscan36.comsys.rwth-aachen.de'],
            country='DE'
                ),
    ]
)

eu_educations: EducationList = EducationList(
    uni_list=[
        Education(
            uni_name='Universität Twente',
            rir_name='SURF B.V.',
            total_ip=3,
            ports=['53'],
            dns_value=['192-87-173-76.measurements.dacs.utwente.nl', 'reactive-measurements.dacs.utwente.nl', 'please.visit.www.openintel.nl', ],
            country='NL'
        ),
        Education(
            uni_name='University of Southern Denmark',
            rir_name='Forskningsnettet - Danish network for Research and Education',
            total_ip=1,
            ports=['53'],
            dns_value=['srv-d1.sdu.dk'],
            country='DK'
                ),
        Education(
            uni_name='Technischen Universität Dänemark',
            rir_name='Forskningsnettet - Danish network for Research and Education',
            total_ip=1,
            ports=['7400', '5683'],
            dns_value=['dtuscanner.compute.dtu.dk'],
            country='DK'
                ),
        Education(
            uni_name='University of Cambridge',
            rir_name='Jisc Services Limited',
            total_ip=1,
            ports=['7', '111', '1900', '123', '17', '389'],
            dns_value=['cccc-scanner.cl.cam.ac.uk', 'internet.wide.scan.using.dns-oarc.blacklist.cl.cam.ac.uk', 'email-cccc-infra--cccc-scanner.cst.cam.ac.uk'],
            country='GB'
                ),
        Education(
            uni_name='Université Grenoble Alpes',
            rir_name='Renater',
            total_ip=1,
            ports=['53'],
            dns_value=['aix.u-ga.fr'],
            country='FR'
                ),
    ]
)

world_educations: EducationList = EducationList(
    uni_list=[
        Education(
            uni_name='Technische Hochschule Georgia',
            rir_name='Georgia Institute of Technology',
            total_ip=3,
            ports=['53'],
            dns_value=[],
            country='US'
        ),
        Education(
            uni_name='Tigard-Tualatin School District',
            rir_name='Multnomah Education Service District',
            total_ip=1,
            ports=['500'],
            dns_value=['autohost66-154-208-12.ttsd.k12.or.us'],
            country='US'
                ),
        Education(
            uni_name='National Institute of Technology Karnataka',
            rir_name='NATIONAL INSTITUTE OF TECHNOLOGY KARNATAKA',
            total_ip=1,
            ports=['8853', '784', '853'],
            dns_value=['nitk-gw2-up-3.nitk.ac.in'],
            country='IN'
                ),
        Education(
            uni_name='',
            rir_name='China Education and Research Network Center',
            total_ip=1,
            ports=['53'],
            dns_value=[],
            country='CN'
                ),
        Education(
            uni_name='Stanford University',
            rir_name='Stanford University',
            total_ip=1,
            ports=['53'],
            dns_value=['research.esrg.stanford.edu'],
            country='US'
                ),
    ]
)


def calc_scan_education(conn_udp: pd.DataFrame):
    result_df: pd.DataFrame = pd.DataFrame()
    for education_data in [de_educations, eu_educations, world_educations]:
        result_df = pd.concat([result_df, _education_scan(education_data, conn_udp)])
    result_df = result_df.reset_index(drop=True)
    return result_df


def _education_scan(education_data: EducationList, conn_udp: pd.DataFrame):
    education_df: pd.DataFrame = pd.DataFrame({
        'Universität': pd.Series(dtype='str'),
        'Land': pd.Series(dtype='str'),
        "Anzahl IP's": pd.Series(dtype='str'),
        "RIR Name": pd.Series(dtype='str'),
        "DNS Eintrag": pd.Series(dtype='str'),
        "Ports": pd.Series(dtype='str'),
    })

    for education in education_data.uni_list:

        new_row: pd.DataFrame = pd.DataFrame({
            'Universität': [education.uni_name],
            'Land': [education.country],
            "Anzahl IP's": [education.total_ip],
            'RIR Name': [education.rir_name],
            'DNS Eintrag': [", ".join(education.dns_value) if education.dns_value else None],
            'Ports': [", ".join(education.ports) if education.ports else None],
        })
        education_df = pd.concat([education_df, new_row], ignore_index=True)

    return education_df