import logging
from typing import Any

logger = logging.getLogger("PredictX.Agent.MaintenancePlanner")


class MaintenancePlannerAgent:
    """
    Maintenance Planner Agent.
    Synthesizes actionable engineering Work Orders with step-by-step Standard Operating
    Procedures (SOPs), required replacement parts, tooling, and downtime estimates.
    """

    REMEDIATION_PLANS = {
        "Bearing Wear / Shaft Misalignment": {
            "work_order_title": "Emergency Bearing Replacement & Shaft Realignment",
            "priority": "EMERGENCY - IMMEDIATE SHUTDOWN",
            "estimated_downtime_hours": 2.5,
            "required_parts": [
                {"part_no": "SKF-6205-2RSH", "desc": "Deep Groove Ball Bearing", "qty": 2},
                {"part_no": "MOBILUX-EP2", "desc": "Lithium Complex Industrial Grease", "qty": "1 Cartridge"},
            ],
            "required_tools": [
                "Mechanical Three-Arm Bearing Puller",
                "Dial Indicator for Shaft Runout",
                "Torque Wrench (Range 20-150 Nm)",
            ],
            "action_steps": [
                "1. Isolate machine power and apply Lock-Out / Tag-Out (LOTO) padlock.",
                "2. Remove bearing housing protective shroud and clean shaft coupling.",
                "3. Extract worn ball bearings using bearing puller without scoring shaft surface.",
                "4. Clean housing cavity and pack new SKF-6205 bearings with fresh lithium grease.",
                "5. Reassemble housing, retorque foundation bolts to 95 Nm, and remove LOTO.",
                "6. Perform 15-minute vibration test run to confirm RMS vibration < 1.5 mm/s.",
            ],
        },
        "Thermal Dissipation / Cooling System Failure": {
            "work_order_title": "Cooling System Overhaul & Radiator Descaling",
            "priority": "HIGH - WITHIN 4 HOURS",
            "estimated_downtime_hours": 1.5,
            "required_parts": [
                {"part_no": "COOLANT-SYN-50", "desc": "Industrial Synthetic Glycol Coolant", "qty": "5 Liters"},
                {"part_no": "FLT-RAD-04", "desc": "Radiator Intake Air Filter", "qty": 2},
            ],
            "required_tools": ["Industrial HEPA Vacuum", "Coolant Refractometer", "Pressure Washer"],
            "action_steps": [
                "1. Power down thermal drive unit and allow surface temp to drop below 40°C.",
                "2. Vacuum external radiator intake filters and replace saturated mesh.",
                "3. Flush cooling lines and inspect circulation pump impeller for debris.",
                "4. Refill reservoir with 50/50 synthetic coolant and bleed air pockets.",
                "5. Validate cooling fan activation temperature trigger at 65°C.",
            ],
        },
        "Hydraulic Chamber Seal Rupture": {
            "work_order_title": "Hydraulic Seal Replacement & Pressure Chamber Calibration",
            "priority": "HIGH - SCHEDULED DOWNTIME",
            "estimated_downtime_hours": 2.0,
            "required_parts": [
                {"part_no": "VITON-ORING-SET", "desc": "High-Pressure Viton O-Ring Gaskets", "qty": 1},
                {"part_no": "HYD-OIL-ISO46", "desc": "Anti-Wear Hydraulic Fluid ISO VG 46", "qty": "10 Liters"},
            ],
            "required_tools": ["Calibrated Torque Wrench (120 Nm)", "O-Ring Extraction Tool", "Pressure Gauge"],
            "action_steps": [
                "1. Depressurize hydraulic circuit and lock relief valves.",
                "2. Unbolt chamber manifold and inspect sealing surfaces for scoring.",
                "3. Replace damaged Viton O-ring seals with lubricated replacements.",
                "4. Retorque all chamber flange bolts to 120 Nm in cross-pattern sequence.",
                "5. Pressurize system and verify steady hold at 100 PSI with zero leakage.",
            ],
        },
    }

    def generate_plan(self, rca_report: dict[str, Any]) -> dict[str, Any]:
        """
        Generates a comprehensive maintenance plan and work order.
        """
        failure_mode = rca_report.get("primary_failure_mode", "")
        plan = self.REMEDIATION_PLANS.get(failure_mode, {
            "work_order_title": f"Routine Maintenance Check: {failure_mode}",
            "priority": "ROUTINE",
            "estimated_downtime_hours": 1.0,
            "required_parts": [{"part_no": "GENERIC-MAINT-KIT", "desc": "Standard Inspection Kit", "qty": 1}],
            "required_tools": ["Standard Hand Tool Kit", "Multimeter"],
            "action_steps": [
                "1. Inspect equipment operational state.",
                "2. Clean foreign debris and verify lubrication levels.",
                "3. Log sensor baseline readings.",
            ],
        })

        work_order = {
            "agent": "MaintenancePlannerAgent",
            "work_order_title": plan["work_order_title"],
            "priority_level": plan["priority"],
            "estimated_downtime_hours": plan["estimated_downtime_hours"],
            "required_parts": plan["required_parts"],
            "required_tools": plan["required_tools"],
            "action_steps": plan["action_steps"],
        }

        logger.info(f"Maintenance Planner generated work order: '{plan['work_order_title']}' ({plan['priority']})")
        return work_order
