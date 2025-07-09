import numpy as np
import math
from typing import Dict, Tuple, List

class AngleCalculator:
    """Utility class for calculating posture-related angles and measurements"""
    
    def calculate_angle(self, point1: Dict, point2: Dict, point3: Dict) -> float:
        """Calculate angle between three points"""
        # Convert to numpy arrays
        p1 = np.array([point1['x'], point1['y']])
        p2 = np.array([point2['x'], point2['y']])
        p3 = np.array([point3['x'], point3['y']])
        
        # Calculate vectors
        v1 = p1 - p2
        v2 = p3 - p2
        
        # Handle edge case where vectors are zero
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0  # Return 0 for degenerate cases
        
        # Calculate angle
        cos_angle = np.dot(v1, v2) / (norm_v1 * norm_v2)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)  # Prevent numerical errors
        angle = np.arccos(cos_angle)
        
        return math.degrees(angle)
    
    def calculate_distance(self, point1: Dict, point2: Dict) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1['x'] - point2['x'])**2 + (point1['y'] - point2['y'])**2)
    
    def calculate_midpoint(self, point1: Dict, point2: Dict) -> Dict:
        """Calculate midpoint between two points"""
        return {
            'x': (point1['x'] + point2['x']) / 2,
            'y': (point1['y'] + point2['y']) / 2
        }
    
    def calculate_pelvic_tilt(self, left_hip: Dict, right_hip: Dict) -> float:
        """Calculate pelvic tilt angle"""
        # Calculate angle of hip line relative to horizontal
        dx = right_hip['x'] - left_hip['x']
        dy = right_hip['y'] - left_hip['y']
        
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        
        # Normalize to anterior/posterior tilt
        return abs(angle_deg)
    
    def calculate_thoracic_kyphosis(self, left_shoulder: Dict, right_shoulder: Dict, 
                                  left_hip: Dict, right_hip: Dict) -> float:
        """Calculate thoracic kyphosis angle"""
        # Midpoints
        shoulder_mid = self.calculate_midpoint(left_shoulder, right_shoulder)
        hip_mid = self.calculate_midpoint(left_hip, right_hip)
        
        # Calculate trunk angle
        dx = shoulder_mid['x'] - hip_mid['x']
        dy = shoulder_mid['y'] - hip_mid['y']
        
        if dy == 0:
            return 0.0  # Avoid division by zero
        
        trunk_angle = math.degrees(math.atan2(abs(dx), abs(dy)))
        
        # Thoracic kyphosis should be in reasonable range (0-60 degrees)
        return min(60, max(0, trunk_angle))
    
    def calculate_cervical_lordosis(self, nose: Dict, left_ear: Dict, right_ear: Dict,
                                  left_shoulder: Dict, right_shoulder: Dict) -> float:
        """Calculate cervical lordosis (head-neck alignment)"""
        # Calculate ear midpoint
        ear_mid = self.calculate_midpoint(left_ear, right_ear)
        
        # Calculate shoulder midpoint
        shoulder_mid = self.calculate_midpoint(left_shoulder, right_shoulder)
        
        # Calculate head angle relative to shoulders
        head_vector = {'x': nose['x'] - ear_mid['x'], 'y': nose['y'] - ear_mid['y']}
        neck_vector = {'x': ear_mid['x'] - shoulder_mid['x'], 'y': ear_mid['y'] - shoulder_mid['y']}
        
        # Calculate angle between head and neck vectors
        dot_product = head_vector['x'] * neck_vector['x'] + head_vector['y'] * neck_vector['y']
        
        head_mag = math.sqrt(head_vector['x']**2 + head_vector['y']**2)
        neck_mag = math.sqrt(neck_vector['x']**2 + neck_vector['y']**2)
        
        if head_mag == 0 or neck_mag == 0:
            return 0
        
        cos_angle = dot_product / (head_mag * neck_mag)
        cos_angle = max(-1, min(1, cos_angle))  # Clamp to valid range
        
        angle = math.degrees(math.acos(cos_angle))
        
        return angle
    
    def calculate_shoulder_height_difference(self, left_shoulder: Dict, right_shoulder: Dict,
                                           image_size: Tuple[int, int]) -> float:
        """Calculate shoulder height difference in cm (estimated)"""
        # Calculate vertical difference (normalized coordinates are 0-1)
        height_diff_normalized = abs(left_shoulder['y'] - right_shoulder['y'])
        
        # Convert to approximate cm (assuming average person height ~170cm)
        # Since coordinates are normalized, multiply by image height first
        height_diff_pixels = height_diff_normalized * image_size[1]
        pixels_per_cm = image_size[1] / 170  # Approximate conversion
        height_diff_cm = height_diff_pixels / pixels_per_cm
        
        return height_diff_cm
    
    def calculate_head_forward_posture(self, nose: Dict, left_ear: Dict, right_ear: Dict,
                                     left_shoulder: Dict, right_shoulder: Dict) -> float:
        """Calculate head forward posture distance"""
        # Calculate ear midpoint
        ear_mid = self.calculate_midpoint(left_ear, right_ear)
        
        # Calculate shoulder midpoint
        shoulder_mid = self.calculate_midpoint(left_shoulder, right_shoulder)
        
        # Calculate horizontal distance between ear and shoulder vertical line
        horizontal_offset = abs(ear_mid['x'] - shoulder_mid['x'])
        
        # Convert to approximate cm (rough estimation)
        forward_distance_cm = horizontal_offset * 100  # Scale factor for cm
        
        return forward_distance_cm
    
    def calculate_lumbar_lordosis(self, left_shoulder: Dict, right_shoulder: Dict,
                                left_hip: Dict, right_hip: Dict) -> float:
        """Calculate lumbar lordosis angle"""
        # This is a simplified calculation
        # In a full implementation, you'd need more spine landmarks
        
        shoulder_mid = self.calculate_midpoint(left_shoulder, right_shoulder)
        hip_mid = self.calculate_midpoint(left_hip, right_hip)
        
        # Calculate trunk alignment
        trunk_angle = math.degrees(math.atan2(
            shoulder_mid['x'] - hip_mid['x'],
            hip_mid['y'] - shoulder_mid['y']
        ))
        
        # Lumbar lordosis is related to trunk curvature
        return abs(trunk_angle) + 30  # Add baseline lordosis
    
    def calculate_scapular_protraction(self, left_shoulder: Dict, right_shoulder: Dict,
                                     left_elbow: Dict, right_elbow: Dict) -> float:
        """Calculate scapular protraction"""
        # Calculate shoulder width
        shoulder_width = self.calculate_distance(left_shoulder, right_shoulder)
        
        # Calculate elbow width
        elbow_width = self.calculate_distance(left_elbow, right_elbow)
        
        # Protraction ratio (simplified calculation)
        if shoulder_width == 0:
            return 0
        
        protraction_ratio = elbow_width / shoulder_width
        
        # Convert to approximate cm measurement
        protraction_cm = max(0, (protraction_ratio - 0.8) * 10)  # Baseline adjustment
        
        return protraction_cm
    
    def calculate_trunk_lateral_deviation(self, nose: Dict, left_hip: Dict, right_hip: Dict) -> float:
        """Calculate trunk lateral deviation"""
        # Calculate hip midpoint
        hip_mid = self.calculate_midpoint(left_hip, right_hip)
        
        # Calculate horizontal deviation of head from hip center
        lateral_deviation = abs(nose['x'] - hip_mid['x'])
        
        # Convert to approximate cm
        deviation_cm = lateral_deviation * 100  # Scale factor
        
        return deviation_cm
    
    def calculate_knee_valgus_varus(self, left_hip: Dict, left_knee: Dict, left_ankle: Dict,
                                   right_hip: Dict, right_knee: Dict, right_ankle: Dict) -> Dict[str, float]:
        """Calculate knee valgus/varus angles"""
        # Left leg angle
        left_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
        
        # Right leg angle  
        right_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
        
        # Convert to valgus/varus (deviation from 180 degrees)
        left_deviation = abs(180 - left_angle)
        right_deviation = abs(180 - right_angle)
        
        return {
            'left_knee_angle': left_deviation,
            'right_knee_angle': right_deviation
        }
    
    def calculate_foot_arch_height(self, left_heel: Dict, left_foot_index: Dict,
                                 right_heel: Dict, right_foot_index: Dict) -> Dict[str, float]:
        """Calculate estimated foot arch height"""
        # This is a simplified 2D calculation
        # In practice, you'd need more foot landmarks
        
        left_arch = abs(left_foot_index['y'] - left_heel['y'])
        right_arch = abs(right_foot_index['y'] - right_heel['y'])
        
        return {
            'left_arch_height': left_arch * 10,  # Scale to approximate cm
            'right_arch_height': right_arch * 10
        }
    
    def calculate_knee_valgus_varus_enhanced(self, left_hip: Dict, left_knee: Dict, left_ankle: Dict,
                                           right_hip: Dict, right_knee: Dict, right_ankle: Dict) -> Dict[str, float]:
        """Enhanced knee valgus/varus calculation with clinical accuracy"""
        
        # Calculate Q-angle (quadriceps angle) for each leg
        left_q_angle = self._calculate_q_angle(left_hip, left_knee, left_ankle)
        right_q_angle = self._calculate_q_angle(right_hip, right_knee, right_ankle)
        
        # Calculate knee alignment angles
        left_knee_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
        right_knee_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
        
        # Determine valgus (knock-knee) or varus (bow-leg) deviation
        # Normal knee angle should be close to 180 degrees
        left_deviation = 180 - left_knee_angle
        right_deviation = 180 - right_knee_angle
        
        # Classify deviation type
        left_type = "valgus" if left_deviation > 0 else "varus"
        right_type = "valgus" if right_deviation > 0 else "varus"
        
        return {
            'left_knee_deviation': abs(left_deviation),
            'right_knee_deviation': abs(right_deviation),
            'left_knee_type': left_type,
            'right_knee_type': right_type,
            'left_q_angle': left_q_angle,
            'right_q_angle': right_q_angle,
            'average_deviation': (abs(left_deviation) + abs(right_deviation)) / 2
        }
    
    def _calculate_q_angle(self, hip: Dict, knee: Dict, ankle: Dict) -> float:
        """Calculate Q-angle (quadriceps angle)"""
        # Q-angle is the angle between the quadriceps and patellar tendon
        # Simplified calculation using hip-knee-ankle alignment
        
        # Calculate vectors
        hip_to_knee = np.array([knee['x'] - hip['x'], knee['y'] - hip['y']])
        knee_to_ankle = np.array([ankle['x'] - knee['x'], ankle['y'] - knee['y']])
        
        # Calculate angle between vectors
        norm_hk = np.linalg.norm(hip_to_knee)
        norm_ka = np.linalg.norm(knee_to_ankle)
        
        if norm_hk == 0 or norm_ka == 0:
            return 0.0
        
        cos_angle = np.dot(hip_to_knee, knee_to_ankle) / (norm_hk * norm_ka)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        
        q_angle = math.degrees(math.acos(cos_angle))
        
        # Normal Q-angle is 10-15 degrees for males, 15-20 for females
        return abs(180 - q_angle)  # Convert to deviation from straight
    
    def calculate_heel_inclination(self, left_heel: Dict, left_ankle: Dict, left_foot_index: Dict,
                                 right_heel: Dict, right_ankle: Dict, right_foot_index: Dict) -> Dict[str, float]:
        """Calculate heel inclination angles"""
        
        # Calculate heel inclination for each foot
        left_inclination = self._calculate_single_heel_inclination(left_heel, left_ankle, left_foot_index)
        right_inclination = self._calculate_single_heel_inclination(right_heel, right_ankle, right_foot_index)
        
        return {
            'left_heel_inclination': left_inclination,
            'right_heel_inclination': right_inclination,
            'average_inclination': (left_inclination + right_inclination) / 2,
            'inclination_difference': abs(left_inclination - right_inclination)
        }
    
    def _calculate_single_heel_inclination(self, heel: Dict, ankle: Dict, foot_index: Dict) -> float:
        """Calculate heel inclination for a single foot"""
        
        # Calculate the angle of the heel relative to the ground
        # Using heel-ankle-foot_index triangle
        
        # Create a horizontal reference line at heel level
        heel_horizontal = {'x': heel['x'] + 0.1, 'y': heel['y']}
        
        # Calculate angle between heel-ankle line and horizontal
        heel_angle = self.calculate_angle(heel_horizontal, heel, ankle)
        
        # Calculate foot angle using heel and toe
        foot_angle = self.calculate_angle(heel, foot_index, ankle)
        
        # Heel inclination is the deviation from normal stance
        inclination = abs(heel_angle - 90)  # 90 degrees would be vertical
        
        return min(45, inclination)  # Cap at 45 degrees for realistic values
    
    def calculate_seated_posture_metrics(self, landmarks: Dict) -> Dict[str, float]:
        """Calculate posture metrics specifically for seated position"""
        
        # Get key landmarks
        nose = landmarks.get('nose')
        left_ear = landmarks.get('left_ear')
        right_ear = landmarks.get('right_ear')
        left_shoulder = landmarks.get('left_shoulder')
        right_shoulder = landmarks.get('right_shoulder')
        left_hip = landmarks.get('left_hip')
        right_hip = landmarks.get('right_hip')
        
        if not all([nose, left_shoulder, right_shoulder, left_hip, right_hip]):
            return {}
        
        # Calculate midpoints
        ear_mid = self.calculate_midpoint(left_ear, right_ear) if left_ear and right_ear else None
        shoulder_mid = self.calculate_midpoint(left_shoulder, right_shoulder)
        hip_mid = self.calculate_midpoint(left_hip, right_hip)
        
        # Seated pelvic tilt
        seated_pelvic_tilt = self._calculate_seated_pelvic_tilt(left_hip, right_hip, left_shoulder, right_shoulder)
        
        # Head-neck position in seated posture
        head_neck_position = self._calculate_seated_head_neck_position(nose, ear_mid, shoulder_mid)
        
        # Forward/backward lean
        trunk_lean = self._calculate_seated_trunk_lean(shoulder_mid, hip_mid)
        
        # Lateral (side-to-side) lean
        lateral_lean = self._calculate_seated_lateral_lean(nose, shoulder_mid, hip_mid)
        
        # Shoulder elevation in seated position
        shoulder_elevation = self.calculate_shoulder_height_difference(left_shoulder, right_shoulder, (1, 1))
        
        return {
            'seated_pelvic_tilt': seated_pelvic_tilt,
            'head_neck_position': head_neck_position,
            'trunk_forward_lean': trunk_lean['forward'],
            'trunk_backward_lean': trunk_lean['backward'],
            'lateral_lean': lateral_lean,
            'shoulder_elevation': shoulder_elevation
        }
    
    def _calculate_seated_pelvic_tilt(self, left_hip: Dict, right_hip: Dict, 
                                    left_shoulder: Dict, right_shoulder: Dict) -> float:
        """Calculate pelvic tilt in seated position"""
        
        # In seated position, pelvic tilt is relative to trunk orientation
        hip_mid = self.calculate_midpoint(left_hip, right_hip)
        shoulder_mid = self.calculate_midpoint(left_shoulder, right_shoulder)
        
        # Calculate trunk angle
        trunk_angle = math.degrees(math.atan2(
            shoulder_mid['x'] - hip_mid['x'],
            hip_mid['y'] - shoulder_mid['y']
        ))
        
        # Pelvic tilt is the deviation from vertical (0 degrees)
        pelvic_tilt = abs(trunk_angle)
        
        return min(45, pelvic_tilt)  # Cap at 45 degrees
    
    def _calculate_seated_head_neck_position(self, nose: Dict, ear_mid: Dict, shoulder_mid: Dict) -> float:
        """Calculate head-neck position in seated posture"""
        
        if not ear_mid:
            # Fallback: use nose-shoulder relationship
            horizontal_offset = abs(nose['x'] - shoulder_mid['x'])
            return horizontal_offset * 50  # Scale factor
        
        # Calculate head forward position relative to shoulders
        head_forward = abs(ear_mid['x'] - shoulder_mid['x'])
        
        # Calculate neck angle
        neck_angle = self.calculate_angle(shoulder_mid, ear_mid, nose)
        
        # Combine forward position and neck angle
        head_neck_score = (head_forward * 30) + (abs(neck_angle - 90) * 0.5)
        
        return min(20, head_neck_score)  # Cap at 20 for seated posture
    
    def _calculate_seated_trunk_lean(self, shoulder_mid: Dict, hip_mid: Dict) -> Dict[str, float]:
        """Calculate trunk lean in seated position"""
        
        # Calculate trunk angle relative to vertical
        trunk_angle = math.degrees(math.atan2(
            shoulder_mid['x'] - hip_mid['x'],
            hip_mid['y'] - shoulder_mid['y']
        ))
        
        # Determine forward or backward lean
        if trunk_angle > 0:
            forward_lean = abs(trunk_angle)
            backward_lean = 0
        else:
            forward_lean = 0
            backward_lean = abs(trunk_angle)
        
        return {
            'forward': min(45, forward_lean),
            'backward': min(30, backward_lean)
        }
    
    def _calculate_seated_lateral_lean(self, nose: Dict, shoulder_mid: Dict, hip_mid: Dict) -> float:
        """Calculate lateral (side-to-side) lean in seated position"""
        
        # Calculate the alignment of head-shoulders-hips
        head_shoulder_offset = abs(nose['x'] - shoulder_mid['x'])
        shoulder_hip_offset = abs(shoulder_mid['x'] - hip_mid['x'])
        
        # Average lateral deviation
        lateral_deviation = (head_shoulder_offset + shoulder_hip_offset) / 2
        
        # Convert to degrees (approximate)
        lateral_lean = lateral_deviation * 45  # Scale factor
        
        return min(30, lateral_lean)  # Cap at 30 degrees for seated posture