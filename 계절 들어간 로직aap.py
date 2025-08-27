def get_morning_routine_structure(db, skin_type, concerns, current_season, makeup='no'):
    """5가지 피부 타입과 주요 고민에 따른 아침 루틴을 구조화하여 추천합니다."""
    steps = []
    user_concerns = {c['name'] for c in concerns if c.get('name')}
    
    # ------------------- 공통 로직 -------------------
    step2_query, step2_params, step2_desc = None, [], ""
    has_wrinkle_elasticity_concern = '주름' in user_concerns or '탄력' in user_concerns
    has_moisture_concern = '수분' in user_concerns
    has_wrinkle_elasticity_moisture_concern = '주름' in user_concerns or '탄력' in user_concerns and '수분' in user_concerns

    # 계절 -> 피부 고민 : 주름,탄력 (o/x) -> 피부 타입            바꾸기!!!!! 간단하게 보여주기 식으로 만들면 됨.
    # ------------------- 겨울 -------------------  
    if current_season == 'winter': 
        # 고민 : 주름,탄력,수분 -> 안티에이징
        if has_wrinkle_elasticity_moisture_concern: 
            # ------------------- 💧 건성 (Dry) -------------------
            if skin_type == 'Dry':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습')
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%밀크%' OR name LIKE '%로션%' OR name LIKE '%젤%' OR name LIKE '%워터%') 
                    AND (name LIKE '%히알루론산%' OR name LIKE '%촉촉%' OR name LIKE '%수분%' OR name LIKE '%약산성%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "피부 장벽을 보호하고 수분을 유지해주는 클렌징 제품을 사용하세요.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE main_category = '에센스/앰플/세럼' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습')
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%히알루론산%' OR name LIKE '%촉촉%' OR name LIKE '%수분%' OR name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%레티놀%) 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "안티에이징 제품으로 주름과 탄력을 관리하고, 피부에 촉촉한 수분감을 더하세요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE main_category = '크림' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습')
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%레티놀%'
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "이제 무거운 사용감 걱정 없이 산뜻한 안티에이징으로 하루를 시작하고, 빈틈없이 촉촉한 피부를 느껴보세요.", "primary_recommendation": p3, "alternatives": a3}) 

            # ------------------- ✨ 지성 (Oily) -------------------
            if skin_type == 'Oily':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%티트리%' OR name LIKE '%그린%' OR name LIKE '%약산성%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "피부에 자극을 주지 않으면서도 수분을 남겨주는 젤 타입이나 약산성 클렌저를 사용해 보세요.<br>과도한 세안은 오히려 피부를 건조하게 만들어 유분 분비를 촉진할 수 있습니다.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE main_category = '에센스/앰플/세럼' 
                    AND sub_category IN ('안티에이징', '리페어')                
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%나이아신%' OR name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%리프팅%' OR name LIKE '%비타민%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "세안 후에는 끈적임 없이 가볍게 흡수되는 주름, 탄력 관리 제품으로 유수분 밸런스를 맞춰주세요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE main_category = '크림' 
                    AND sub_category IN ('안티에이징', '리페어')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND name LIKE '%수분 크림%' OR name LIKE '%젤%' OR name LIKE '%워터 크림%' OR name LIKE '%로션%'
                    AND name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%''
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "이제 무거운 사용감 걱정 없이 산뜻한 안티에이징으로 하루를 시작하고, 빈틈없이 촉촉한 피부를 느껴보세요.", "primary_recommendation": p3, "alternatives": a3}) 
                    
            # ------------------- ⚖️ 중성 (Normal) -------------------
            if skin_type == 'Normal':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%약산성%' OR name LIKE '%세이프%' OR name LIKE '%그린%' OR name LIKE '%모닝%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "유수분 밸런스가 깨지지 않도록 가볍게 물세안 또는 순한 클렌저 사용을 추천드립니다.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE main_category In ('스킨/토너') 
                    AND sub_category IN ('안티에이징', '리페어')  
                    AND (name LIKE '%나이아신%' OR name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%리프팅%' OR name LIKE '%비타민%' OR name LIKE '%플러스%' OR name LIKE '%저분자%' OR name LIKE '%캡슐%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "세안 후에는 끈적임 없이 가볍게 흡수되는 주름, 탄력 관리 제품으로 유수분 밸런스를 맞춰주세요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE main_category = '크림' 
                    AND sub_category IN ('안티에이징', '리페어')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%히알루론산%'
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "탄력과 영양을 동시에 채워 탱탱한 피부를 만들어보세요.", "primary_recommendation": p3, "alternatives": a3}) 
            # ------------------- 복합 건성 (CombinationDry) -------------------
            if skin_type == 'CombinationDry':
                # ------------------- 1단계: 아침 세안 -------------------
                    q1 = """
                    SELECT * FROM products WHERE main_category = '클렌징' 
                    AND sub_category IN ('안티에이징', '리페어', '수분', '보습')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND name NOT LIKE '%리치%'
                    AND (name LIKE '%워터%' OR name LIKE '%폼%' OR name LIKE '%클렌저%' OR name LIKE '%젤%') 
                    AND (name LIKE '%약산성%' OR name LIKE '%세이프%' OR name LIKE '%그린%' OR name LIKE '%모닝%' OR name LIKE '%히알루론산%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p1, a1 = get_products_by_query(db, q1)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "유수분 밸런스를 깨뜨리지 않고, 촉촉함은 남기면서 노폐물만 깨끗하게 씻어내는 것이 중요합니다.", "primary_recommendation": p1, "alternatives": a1})
                # ------------------- 2단계: 수분 충전  -------------------
                    q2 = """
                    SELECT * FROM products WHERE main_category In ('스킨/토너', '에센스/앰플/세럼') 
                    AND sub_category IN ('안티에이징', '리페어')  
                    AND (name LIKE '%병풀%' OR name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%리프팅%' OR name LIKE '%비타민%' OR name LIKE '%플러스%' OR name LIKE '%저분자%' OR name LIKE '%캡슐%' OR name LIKE '%수딩%') 
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p2, a2 = get_products_by_query(db, q2)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": "세안 후에는 끈적임 없이 가볍게 흡수되는 주름, 탄력 관리 제품으로 유수분 밸런스를 맞춰주세요.", "primary_recommendation": p2, "alternatives": a2}) 
                # ------------------- 3단계: 보습 & 보호 -------------------
                    q3 = """
                    SELECT * FROM products WHERE main_category = '크림' 
                    AND sub_category IN ('안티에이징', '리페어')  
                    AND name NOT LIKE '%딥%' AND name NOT LIKE '%리치%'
                    AND name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%히알루론산%'
                    ORDER BY rank ASC LIMIT 3"
                    """
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": "탄력과 영양을 동시에 채워 탱탱한 피부를 만들어보세요.", "primary_recommendation": p3, "alternatives": a3}) 
               
            # 복합 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 기본 (Fallback) -- 중성 피부 루틴을 기본 값으로 사용    
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
        # 고민 : 주름,탄력
        elif has_wrinkle_elasticity_moisture_concern: 
                # 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
                # 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 중성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 기본 (Fallback) -- 중성 피부 루틴을 기본 값으로 사용    
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
                
        # 고민 : 수분
        elif has_moisture_concern: 
                # 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
                # 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 중성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 기본 (Fallback) -- 중성 피부 루틴을 기본 값으로 사용    
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호             
        # 고민 : 없음
        else: 
            # 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
                # 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 중성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 기본 (Fallback) -- 중성 피부 루틴을 기본 값으로 사용    
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
                
     # ------------------- 여름 -------------------            
    elif current_season == 'summer':  # 피부고민 순위 : 주름,탄력 + 수분 > 주름,탄력 > 수분            
        # 고민 : 주름,탄력,수분
        if has_wrinkle_elasticity_moisture_concern: 
            # 건성
            if skin_type == 'Dry':
                # 1단계: 아침 세안
                q1 = "SELECT * FROM products WHERE main_category = '클렌징' AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND (name LIKE '%밀크%' OR name LIKE '%로션%' OR name LIKE '%폼%' OR name LIKE '%젤%' OR name LIKE '%워터%') AND (name LIKE '%히알루론산%' OR name LIKE '%촉촉%' OR name LIKE '%수분%' OR name LIKE '%약산성%') ORDER BY rank ASC LIMIT 3"
                p1, a1 = get_products_by_query(db, q1)
                steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "순한 약산성 클렌저로 자극없이 부드럽게 세안하세요.", "primary_recommendation": p1, "alternatives": a1})
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 중성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 기본 (Fallback) -- 중성 피부 루틴을 기본 값으로 사용    
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
        # 고민 : 주름,탄력
        elif has_wrinkle_elasticity_moisture_concern: 
                # 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
                # 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 중성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 기본 (Fallback) -- 중성 피부 루틴을 기본 값으로 사용    
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
                
        # 고민 : 수분
        elif has_moisture_concern: 
                # 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
                # 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 중성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 기본 (Fallback) -- 중성 피부 루틴을 기본 값으로 사용    
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호             
        # 고민 : 없음
        else: 
            # 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
                # 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 중성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 기본 (Fallback) -- 중성 피부 루틴을 기본 값으로 사용    
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호    
                
 # ------------------- 환절기 -------------------            
    else:  # 피부고민 순위 : 주름,탄력 + 수분 > 주름,탄력 > 수분            
        # 고민 : 주름,탄력,수분
        if has_wrinkle_elasticity_moisture_concern: 
            # 건성
            if skin_type == 'Dry':
                # 1단계: 아침 세안
                q1 = "SELECT * FROM products WHERE main_category = '클렌징' AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND (name LIKE '%밀크%' OR name LIKE '%로션%' OR name LIKE '%폼%' OR name LIKE '%젤%' OR name LIKE '%워터%') AND (name LIKE '%히알루론산%' OR name LIKE '%촉촉%' OR name LIKE '%수분%' OR name LIKE '%약산성%') ORDER BY rank ASC LIMIT 3"
                p1, a1 = get_products_by_query(db, q1)
                steps.append({"step_title": "STEP 1. 아침 세안", "step_description": "순한 약산성 클렌저로 자극없이 부드럽게 세안하세요.", "primary_recommendation": p1, "alternatives": a1})
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 중성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 기본 (Fallback) -- 중성 피부 루틴을 기본 값으로 사용    
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
        # 고민 : 주름,탄력
        elif has_wrinkle_elasticity_moisture_concern: 
                # 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
                # 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 중성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 기본 (Fallback) -- 중성 피부 루틴을 기본 값으로 사용    
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
                
        # 고민 : 수분
        elif has_moisture_concern: 
                # 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
                # 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 중성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 기본 (Fallback) -- 중성 피부 루틴을 기본 값으로 사용    
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호             
        # 고민 : 없음
        else: 
            # 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
                # 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 중성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 건성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 복합 지성
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호
            # 기본 (Fallback) -- 중성 피부 루틴을 기본 값으로 사용    
                # 1단계: 아침 세안
                # 2단계: 수분 충전 (고민에 따라 분기)   
                # 3단계: 보습 & 보호    
                
                      
                    # 1단계: 아침 세안
                    step1_desc = "순한 약산성 클렌저로 자극없이 부드럽게 세안하세요."
                    step1_query = "SELECT * FROM products WHERE main_category = '클렌징' AND name NOT LIKE '%딥%' AND name NOT LIKE '%오일%' AND name NOT LIKE '%팩%' AND (name LIKE '%밀크%' OR name LIKE '%로션%' OR name LIKE '%폼%' OR name LIKE '%젤%' OR name LIKE '%워터%') AND (name LIKE '%히알루론산%' OR name LIKE '%촉촉%' OR name LIKE '%수분%' OR name LIKE '%약산성%') ORDER BY rank ASC LIMIT 3"
                    p1, a1 = get_products_by_query(db, step1_query, step1_desc)
                    steps.append({"step_title": "STEP 1. 아침 세안", "step_description": step1_desc, "primary_recommendation": p1, "alternatives": a1})

                    # 2단계: 수분 충전 (고민에 따라 분기)
                    if not step2_query: # 특정 고민이 없을 경우
                        step2_desc = "점성이 있는 에센스나 앰플로 깊은 수분감을 채워주세요."
                        step2_query = "SELECT * FROM products WHERE main_category = '스킨케어' AND middle_category = '에센스/앰플/세럼' AND sub_category IN ('보습', '수분', '진정') AND (name LIKE '%히알루론산%' OR name LIKE '%판테놀%' OR name LIKE '%글리세린%' OR name LIKE '%수분%') ORDER BY rank ASC LIMIT 3"
                    p2, a2 = get_products_by_query(db, step2_query, step2_params)
                    steps.append({"step_title": "STEP 2. 집중 케어", "step_description": step2_desc, "primary_recommendation": p2, "alternatives": a2})

                    # 3단계: 보습 & 보호
                    if not step3_query:
                        step3_desc="꾸덕한 보습 크림으로 수분 보호막을 만들어주세요."
                        step2_query= "SELECT * FROM products WHERE main_category = '스킨케어' AND middle_category = '크림' AND sub_category In ('보습', '수분', '진정') AND (name LIKE '%밤%' OR name LIKE '%리치%' OR name LIKE '%세라마이드%' OR name LIKE '%시어버터%' OR name LIKE '%스쿠알렌%') ORDER BY rank ASC LIMIT 3"
                    p3, a3 = get_products_by_query(db, q3)
                    steps.append({"step_title": "STEP 3. 보습 & 보호", "step_description": step3_desc, "primary_recommendation": p3, "alternatives": a3})

            # ------------------- ✨ 지성 (Oily) -------------------

                step2_desc = "아침에도 가볍게 사용하는 안티에이징 제품으로 주름과 탄력을 관리하고, 피부에 촉촉한 수분감을 더하세요."
                step2_query = """SELECT * FROM products 
                                WHERE main_category = '스킨케어' AND middle_category = '에센스/앰플/세럼' 
                                AND sub_category IN ('안티에이징', '리페어', '수분', '보습') 
                                AND name NOT LIKE '%나이트%' AND name NOT LIKE '%리치%' 
                                AND name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%레티놀%'
                                ORDER BY rank ASC LIMIT 3"""
                step3_desc = "이제 무거운 사용감 걱정 없이 산뜻한 안티에이징으로 하루를 시작하고, 빈틈없이 촉촉한 피부를 느껴보세요."
                step3_query = """SELECT * FROM products 
                                WHERE main_category = '스킨케어' AND middle_category = '크림' 
                                AND sub_category IN ('안티에이징', '리페어', '수분', '보습') 
                                AND name NOT LIKE '%나이트%' AND name NOT LIKE '%리치%' 
                                AND name LIKE '%펩타이드%' OR name LIKE '%아데노신%' OR name LIKE '%비타민%' OR name LIKE '%나이아신%' OR name LIKE '%레티놀%'                    
                                ORDER BY rank ASC LIMIT 3"""  
                                                
    elif has_wrinkle_elasticity_concern:
        step2_desc = "아침에도 부담 없는 텍스처로 주름과 탄력을 동시에 관리하세요."
        step2_query = """SELECT * FROM products 
                         WHERE main_category = '스킨케어' AND middle_category = '에센스/앰플/세럼' 
                         AND sub_category IN ('안티에이징', '리페어') 
                         AND name NOT LIKE '%나이트%' AND name NOT LIKE '%리치%' 
                         ORDER BY rank ASC LIMIT 3"""
        step3_desc = "주름 개선과 탄력 강화에 효과적인 크림으로 피부에 힘을 불어넣어 주세요"
        step3_query = """SELECT * FROM products 
                         WHERE main_category = '스킨케어' AND middle_category = '크림' 
                         AND sub_category IN ('안티에이징', '리페어') 
                         AND name NOT LIKE '%나이트%' AND name NOT LIKE '%리치%' 
                         AND name LIKE '%펩타이드%' OR OR name LIKE '%아데노신%' OR name LIKE '%콜라겐%' OR name LIKE '%비타민%'
                         ORDER BY rank ASC LIMIT 3"""  
                         
    elif has_moisture_concern:
        step2_desc = "수분감이 풍부한 제품으로 피부 속부터 촉촉함을 채워주세요."
        step2_query = """SELECT * FROM products 
                         WHERE main_category = '스킨케어' AND middle_category = '에센스/앰플/세럼' 
                         AND sub_category IN ('수분', '보습') 
                         AND name LIKE '%비타민%' OR OR name LIKE '%펩타이드%' OR name LIKE '%나이아신%' OR name LIKE '%히알루론산%'
                         ORDER BY rank ASC LIMIT 3"""       
        step3_desc = "하루 종일 촉촉한 피부를 위해 가벼우면서도 보습력 있는 크림을 선택하세요."
        step3_query = """SELECT * FROM products 
                         WHERE main_category = '스킨케어' AND middle_category = '크림' 
                         AND sub_category IN ('안티에이징', '리페어') 
                         AND name NOT LIKE '%나이트%' AND name NOT LIKE '%리치%' 
                         AND name LIKE '%세라마이드%' OR OR name LIKE '%코엔자임%' OR name LIKE '%스쿠알란%' OR name LIKE '%촉촉%' OR name LIKE '%히알루론산%'
                         ORDER BY rank ASC LIMIT 3"""
    elif current_season == 'summer': #여름
    
    
    
    else: # 환절기
        
        
        