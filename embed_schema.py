from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

load_dotenv()

# ── PINECONE SETUP ────────────────────────────────────────────────────────────
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

# ── EMBEDDING MODEL ───────────────────────────────────────────────────────────
model = SentenceTransformer("all-MiniLM-L6-v2")

# ── SCHEMA DESCRIPTIONS ───────────────────────────────────────────────────────
# schemas = [
#     {
#         "id": "machine_type",
#         "text": """Table: machine_type
# Columns: mtid (machine type ID), type (machine type name e.g. CLADDING, WELDING, GASCUTTING), created_at, updated_at.
# Use this table to filter machines by their type."""
#     },
#     {
#         "id": "machines",
#         "text": """Table: machines
# Columns: mid (machine ID), name (machine name e.g. Rectifier1, D&H-2), hardware_id, des (description), 
# msid, mtid (links to machine_type), hid, orgid, mcsid, mcid, rpm_multiplication_factor, 
# notify, deleted, created_at, updated_at.
# Use this table to get machine names, IDs, and hardware identifiers."""
#     },
#     {
#         "id": "deviation",
#         "text": """Table: deviation
# Columns: hardware_id (links to machines), oid, shid, start_tm (deviation start time), 
# end_tm (deviation end time), span (duration in seconds), type (high or low), parameter (current, voltage, or gas).
# Use this table to find deviation alerts — when a machine parameter went above or below threshold.
# Filter by type='high' for high alerts, type='low' for low alerts.
# Filter by parameter to get current, voltage, or gas deviations."""
#     },
#     {
#         "id": "machine_derived",
#         "text": """Table: machine_derived
# Columns: business_date, shift_name, machine_type, machine_name, mid, period_start, period_end,
# target_arc_time, active, idle, inrepair, breakdown, target_deposit, deposit, actualcost, 
# partsneedcheckup, interval_batch.
# Use this table for machine performance metrics — arc time, active vs idle time, cost, and maintenance needs.
# Compare active vs target_arc_time for efficiency calculations."""
#     },
#     {
#         "id": "periodic_data_interval2",
#         "text": """Table: periodic_data_interval2
# Columns: business_date, shift_name, machine_type, machine_name, job_name,
# weld_cur (welding current in amps), weld_volt (welding voltage in volts), weld_gas (gas consumption),
# motor_cur (motor current), motor_volt (motor voltage), hs_temp (hot spot temperature),
# amb_temp (ambient temperature), rpm, tm (timestamp), current_deviation_flag, voltage_deviation_flag, gas_deviation_flag.
# Use this table for real-time sensor readings — current, voltage, gas, temperature, RPM per machine per interval."""
#     },
#     {
#         "id": "summarize_clad_details_info",
#         "text": """Table: summarize_clad_details_info
# Columns: business_date, shift_name, oid, machine_type, machine_name, ontime, offtime, time_span,
# on_cur (current when on), off_cur (current when off), avg_weld_cur (average welding current),
# on_volt, off_volt, avg_weld_volt (average welding voltage), on_weight, off_weight, loss_weight.
# Use this table for cladding machine summaries — average current, voltage, weight loss per shift per machine."""
#     },
#     {
#         "id": "summarize_gascutting_machine",
#         "text": """Table: summarize_gascutting_machine
# Columns: business_date, shift_name, machine_type, machine_name, on_time, off_time, time_span,
# net_travel_in_mm (distance travelled in mm), net_lpg_consumption (LPG used in litres),
# net_o2_consumption_meter1, net_o2_consumption_meter2 (O2 consumed), mm_per_min (cutting speed),
# thickness, cut_mm_mtr.
# Use this table for gas cutting machine summaries — LPG consumption, O2 consumption, cutting speed per shift."""
#     },
#     {
#         "id": "summarize_nongascut_machine",
#         "text": """Table: summarize_nongascut_machine
# Columns: business_date, shift_name, machine_type, machine_name, on_time, off_time, time_span,
# total_lpg_cons (total LPG consumed), total_heating_o2 (heating O2 used),
# net_travel_in_mm, mm_per_min.
# Use this table for non-gas cutting machine summaries — LPG, heating O2, travel distance per shift."""
#     },
#     {
#         "id": "user",
#         "text": """Table: user
# Columns: uid, name, email, phno, roleid, hid, orgid, certificate_id, identification_no,
# operator_rfid, deleted, created_at, updated_at, username, active_status.
# Use this table to look up operators and users — who operated which machine, operator details."""
#     },
# ]

schemas = [
    {
        "id": "machine_type",
        "text": """Table: machine_type

PURPOSE:
Master lookup table containing all machine categories used throughout the Industrial IoT monitoring system.

COLUMNS:
- mtid: Machine type identifier.
- type: Machine type name.

KNOWN MACHINE TYPES:
- CLAD
- CLADDING
- GMAW
- WELDING
- GASCUTTING
- GAS CUTTING

RELATIONSHIPS:
- machine_type.mtid = machines.mtid

USE THIS TABLE WHEN USERS ASK:
- What machine types exist?
- List all machine categories.
- Show all machine types.
- Which machine types are available?
- Show cladding machine types.
- Show welding machine types.
- Show gas cutting machine types.
- Which category does this machine belong to?
- What are the different kinds of machines?

SYNONYMS:
- CLAD = CLADDING = RECTIFIER
- GMAW = WELDING
- GASCUTTING = GAS CUTTING

COMMON JOINS:
machine_type → machines
"""
    },

    {
        "id": "machines",
        "text": """Table: machines

PURPOSE:
Master machine inventory containing machine names, machine identifiers, hardware identifiers, descriptions, and machine classifications.

COLUMNS:
- mid: Machine ID.
- name: Machine name.
- hardware_id: Hardware identifier used by telemetry and alert systems.
- des: Machine description.
- msid.
- mtid: Machine type identifier.
- hid.
- orgid.
- mcsid.
- mcid.
- rpm_multiplication_factor.
- notify.
- deleted.
- created_at.
- updated_at.

EXAMPLE MACHINE NAMES:
- Rectifier1
- Rectifier2
- Rectifier3
- D&H-1
- D&H-2
- D&H-9

RELATIONSHIPS:
- machines.mtid = machine_type.mtid
- machines.hardware_id = deviation.hardware_id
- machines.name = periodic_data_interval2.machine_name
- machines.name = machine_derived.machine_name

USE THIS TABLE WHEN USERS ASK:
- Name all machines.
- List all machines.
- Show machine names.
- Show machine IDs.
- Find machine details.
- Find machine descriptions.
- Show machine inventory.
- Which machines exist?
- Show all cladding machines.
- Name all cladding machines.
- List all CLAD machines.
- List all rectifier machines.
- Show all welding machines.
- List all GMAW machines.
- Show all gas cutting machines.
- Which machine has hardware ID X?
- Find details of D&H-2.
- Find details of Rectifier1.
- Find machine by name.
- Which machines belong to CLAD?
- Which machines belong to GMAW?
- Which machines belong to GASCUTTING?

BUSINESS VOCABULARY:
- Rectifier = CLAD machine.
- D&H machines = Welding machines.
- Machine inventory = machines table.

COMMON JOINS:
machines ↔ machine_type
machines ↔ deviation
machines ↔ machine_derived
machines ↔ periodic_data_interval2
"""
    },

    {
        "id": "deviation",
        "text": """Table: deviation

PURPOSE:
Stores alert and deviation events generated whenever machine parameters exceed configured thresholds.

COLUMNS:
- hardware_id: Hardware identifier linked to machines.
- oid.
- shid.
- start_tm: Deviation start timestamp.
- end_tm: Deviation end timestamp.
- span: Deviation duration in seconds.
- type: Alert type (high or low).
- parameter: Parameter causing deviation (current, voltage, gas).

RELATIONSHIPS:
- deviation.hardware_id = machines.hardware_id

USE THIS TABLE WHEN USERS ASK:
- Show alerts.
- Show machine alerts.
- Show alarms.
- Show deviations.
- Which machines generated alerts?
- Which machines triggered alarms?
- List all deviations.
- Count deviations.
- Show current deviations.
- Show voltage deviations.
- Show gas deviations.
- Show high alerts.
- Show low alerts.
- Which machine had the most alerts?
- Which machine exceeded thresholds?
- Which machine exceeded current limits?
- Which machine exceeded voltage limits?
- Which machine had gas deviations?
- Show alert durations.
- Find alert history.
- Show alert trends.

SYNONYMS:
- Alert = Alarm = Deviation = Threshold violation.
- High alert = Above threshold.
- Low alert = Below threshold.

COMMON ANALYTICS:
- Alert count by machine.
- Average alert duration.
- Top alert-generating machines.
- Current vs voltage alert comparison.
- Deviation trends over time.
"""
    },

    {
        "id": "machine_derived",
        "text": """Table: machine_derived

PURPOSE:
Contains shift-level machine utilization, productivity, cost, and maintenance KPIs.

COLUMNS:
- business_date.
- shift_name.
- machine_type.
- machine_name.
- mid.
- period_start.
- period_end.
- target_arc_time.
- active.
- idle.
- inrepair.
- breakdown.
- target_deposit.
- deposit.
- actualcost.
- partsneedcheckup.
- interval_batch.

USE THIS TABLE WHEN USERS ASK:
- Show machine performance.
- Show machine utilization.
- Which machines were active?
- Which machines were idle?
- Which machines broke down?
- Which machines were under repair?
- Show repair statistics.
- Show maintenance KPIs.
- Which machines need maintenance?
- Which machines need checkup?
- Show efficiency.
- Compare active vs idle time.
- Compare target vs actual performance.
- Compare deposit vs target deposit.
- Show machine productivity.
- Show production KPIs.
- Show machine costs.

SYNONYMS:
- Active time = Utilization.
- Breakdown = Failure.
- In repair = Maintenance.
- Efficiency = Target achievement.

COMMON CALCULATIONS:
- Utilization = active / target_arc_time.
- Deposit achievement = deposit / target_deposit.
"""
    },

    {
        "id": "periodic_data_interval2",
        "text": """Table: periodic_data_interval2

PURPOSE:
Main Industrial IoT telemetry table containing periodic sensor readings and real-time machine operating data.

COLUMNS:
- business_date.
- shift_name.
- machine_type.
- machine_name.
- job_name.
- weld_cur: Welding current in amps.
- weld_volt: Welding voltage in volts.
- weld_gas: Gas consumption.
- motor_cur: Motor current.
- motor_volt: Motor voltage.
- hs_temp: Hotspot temperature.
- amb_temp: Ambient temperature.
- rpm: Rotations per minute.
- tm: Timestamp.
- current_deviation_flag.
- voltage_deviation_flag.
- gas_deviation_flag.

RELATIONSHIPS:
- machine_name links to machines.name.

USE THIS TABLE WHEN USERS ASK:
- Show sensor readings.
- Show telemetry.
- Show live machine data.
- Show machine readings.
- Show current readings.
- Show voltage readings.
- Show gas readings.
- Show RPM values.
- Show temperatures.
- What is the current of machine X?
- What is the voltage of machine X?
- What is the RPM of machine X?
- Show telemetry trends.
- Show sensor trends.
- Show readings over time.
- Find average current.
- Find average voltage.
- Find peak current.
- Find peak voltage.
- Show gas consumption trends.
- Show abnormal temperatures.
- Show hotspot temperatures.
- Show ambient temperatures.
- Show machine status during a shift.
- Show machine telemetry for Shift A.
- Show machine telemetry for Shift B.
- Show real-time monitoring data.

SYNONYMS:
- Telemetry = Sensor data = Machine readings = Live data.
- Current = Amps.
- Voltage = Volts.
- RPM = Speed.
- Hotspot temperature = HS temperature.

COMMON ANALYTICS:
- Average current.
- Average voltage.
- Maximum temperature.
- Time-series analysis.
- Trend analysis.
- Sensor anomaly detection.
"""
    },

    {
        "id": "summarize_clad_details_info",
        "text": """Table: summarize_clad_details_info

PURPOSE:
Shift-level production summaries for CLAD (cladding/rectifier) machines.

COLUMNS:
- business_date.
- shift_name.
- oid.
- machine_type.
- machine_name.
- ontime.
- offtime.
- time_span.
- on_cur.
- off_cur.
- avg_weld_cur.
- on_volt.
- off_volt.
- avg_weld_volt.
- on_weight.
- off_weight.
- loss_weight.

USE THIS TABLE WHEN USERS ASK:
- Show cladding summaries.
- Show CLAD summaries.
- Show rectifier summaries.
- Show cladding performance.
- Show rectifier performance.
- Average current for cladding machines.
- Average voltage for cladding machines.
- Which rectifier had the highest current?
- Which rectifier had the highest voltage?
- Compare cladding machine performance.
- Show cladding cycle duration.
- Show weight loss.
- Compare weight loss across machines.
- Show CLAD production KPIs.

SYNONYMS:
- CLAD = Cladding = Rectifier.

COMMON ANALYTICS:
- Average weld current.
- Average weld voltage.
- Weight loss analysis.
- Cycle duration analysis.
"""
    },

    {
        "id": "summarize_gascutting_machine",
        "text": """Table: summarize_gascutting_machine

PURPOSE:
Shift-level production summaries for gas cutting operations.

COLUMNS:
- business_date.
- shift_name.
- machine_type.
- machine_name.
- on_time.
- off_time.
- time_span.
- net_travel_in_mm.
- net_lpg_consumption.
- net_o2_consumption_meter1.
- net_o2_consumption_meter2.
- mm_per_min.
- thickness.
- cut_mm_mtr.

USE THIS TABLE WHEN USERS ASK:
- Show gas cutting summaries.
- Show gas cutting performance.
- Show gas cutting productivity.
- Show cutting speed.
- Show LPG consumption.
- Show oxygen consumption.
- Which gas cutting machine consumed the most LPG?
- Which machine consumed the most oxygen?
- Which machine had the highest cutting speed?
- Compare gas cutting machines.
- Show thickness-wise performance.
- Show cut lengths.
- Show travel distance.
- Show gas cutting KPIs.

SYNONYMS:
- Gas cutting = Flame cutting.

COMMON ANALYTICS:
- Cutting speed analysis.
- LPG consumption analysis.
- Oxygen consumption analysis.
- Productivity comparison.
"""
    },

    {
        "id": "summarize_nongascut_machine",
        "text": """Table: summarize_nongascut_machine

PURPOSE:
Shift-level summaries for non-gas-cutting heating operations.

COLUMNS:
- business_date.
- shift_name.
- machine_type.
- machine_name.
- on_time.
- off_time.
- time_span.
- total_lpg_cons.
- total_heating_o2.
- net_travel_in_mm.
- mm_per_min.

USE THIS TABLE WHEN USERS ASK:
- Show heating summaries.
- Show LPG consumption.
- Show heating oxygen usage.
- Show heating efficiency.
- Compare fuel consumption.
- Compare LPG usage.
- Compare heating oxygen usage.
- Which machine consumed the most LPG?
- Which machine used the most heating oxygen?
- Show travel distance.
- Show productivity.
- Show machine efficiency.

COMMON ANALYTICS:
- LPG consumption trends.
- Heating oxygen trends.
- Productivity comparisons.
"""
    },

    {
        "id": "user",
        "text": """Table: user

PURPOSE:
Stores operator, employee, supervisor, administrator, and user information.

COLUMNS:
- uid.
- name.
- email.
- phno.
- roleid.
- hid.
- orgid.
- certificate_id.
- identification_no.
- operator_rfid.
- deleted.
- created_at.
- updated_at.
- username.
- active_status.

USE THIS TABLE WHEN USERS ASK:
- Show users.
- List users.
- Show operators.
- Show employees.
- Find operator details.
- Find user details.
- Search by RFID.
- Search by username.
- Find operator names.
- Find operator emails.
- Show active users.
- Show inactive users.
- Show administrators.
- Show supervisors.
- Find contact details.
- Show operator information.

SYNONYMS:
- Operator = User = Employee.
- RFID = Operator card.

COMMON ANALYTICS:
- Active user counts.
- User role distribution.
- Operator lookup.
"""
    }
]

# ── EMBED AND UPSERT ──────────────────────────────────────────────────────────
print("Embedding schema descriptions...")

vectors = []
for schema in schemas:
    embedding = model.encode(schema["text"]).tolist()
    vectors.append({
        "id": schema["id"],
        "values": embedding,
        "metadata": {"text": schema["text"], "table": schema["id"]}
    })

index.upsert(vectors=vectors)
print(f"✓ {len(vectors)} table schemas embedded and stored in Pinecone")
print("Done.")