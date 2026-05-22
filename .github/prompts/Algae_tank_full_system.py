import FreeCAD as App
import Part

def create_full_system_cfd_domain():
    # 建立新文件
    doc = App.newDocument("Algae_Tank_Full_System_V2")

    # ==========================================
    # 1. 系統參數設定 PARAMETERS (單位: mm)
    # ==========================================
    # 主缸 (Tank Parameters)
    neck_r = 55.0 / 2.0
    neck_h = 50.0
    shoulder_h = 80.0
    main_r = 270.0 / 2.0
    main_h = 300.0
    
    # 充氣環 (Aeration Ring Parameters)
    ring_major_r = 75.0
    ring_minor_r = 6.0
    ring_z_height = neck_h + 40.0
    
    # 閥門及連接管 (Valve & Connection Parameters)
    valve_r = neck_r
    valve_h = 60.0
    cyclone_offset_x = 150.0  # 旋流器向旁邊平移 150mm，避開主缸正下方
    
    # 水力旋流器 (Hydrocyclone Parameters)
    cylindrical_section_r = 60.0
    cylindrical_section_h = 100.0
    conical_section_h = 150.0
    underflow_r = 10.0          # 底部微藻排出口 (Apex)
    feed_inlet_r = 15.0         # 切向入口半徑
    
    # 精確計算 Y 軸偏移，確保喉管完美切入旋流器外壁
    cyclone_offset_y = -(cylindrical_section_r - feed_inlet_r) # -45.0

    # ==========================================
    # 2. 建立主缸 BUILD THE TANK (由 Z = 0 向上起)
    # ==========================================
    tank_neck = Part.makeCylinder(neck_r, neck_h)
    tank_shoulder = Part.makeCone(neck_r, main_r, shoulder_h, App.Vector(0, 0, neck_h), App.Vector(0, 0, 1))
    tank_main = Part.makeCylinder(main_r, main_h, App.Vector(0, 0, neck_h + shoulder_h), App.Vector(0, 0, 1))
    
    fluid_domain = tank_neck.fuse(tank_shoulder).fuse(tank_main)

    # 3. 挖走充氣環實體 Cut out the Aeration Ring
    feed_pipe_h = (neck_h + shoulder_h + main_h) - ring_z_height + 10.0
    ring = Part.makeTorus(ring_major_r, ring_minor_r, App.Vector(0, 0, ring_z_height), App.Vector(0, 0, 1))
    feed_pipe = Part.makeCylinder(ring_minor_r, feed_pipe_h, App.Vector(ring_major_r, 0, ring_z_height), App.Vector(0, 0, 1))
    aeration_hardware = ring.fuse(feed_pipe)
    
    fluid_domain = fluid_domain.cut(aeration_hardware)

    # ==========================================
    # 4. 建立底部閥門及橫向喉管 BUILD THE VALVE & HORIZONTAL PIPE
    # ==========================================
    z_valve_bottom = -valve_h
    # 垂直向下的閥門空間
    valve_body = Part.makeCylinder(valve_r, valve_h, App.Vector(0, 0, z_valve_bottom), App.Vector(0, 0, 1))
    
    # 橫向引水喉管 (L型彎管)，將水帶到旋流器。長度加 10mm 確保兩端融合無縫
    pipe_horizontal = Part.makeCylinder(feed_inlet_r, cyclone_offset_x + 10.0, App.Vector(0, 0, z_valve_bottom + 20.0), App.Vector(1, 0, 0))
    
    fluid_domain = fluid_domain.fuse(valve_body).fuse(pipe_horizontal)

    # ==========================================
    # 5. 建立水力旋流器 BUILD THE HYDROCYCLONE (於平移位置)
    # ==========================================
    z_cyclone_top = z_valve_bottom + 40.0 
    z_cylindrical_bottom = z_cyclone_top - cylindrical_section_h
    z_conical_bottom = z_cylindrical_bottom - conical_section_h

    # 圓柱體旋流室 (中心點位於 X=150, Y=-45)
    cylindrical_section = Part.makeCylinder(cylindrical_section_r, cylindrical_section_h, App.Vector(cyclone_offset_x, cyclone_offset_y, z_cylindrical_bottom), App.Vector(0, 0, 1))
    
    # 圓錐體部分
    conical_section = Part.makeCone(cylindrical_section_r, underflow_r, conical_section_h, App.Vector(cyclone_offset_x, cyclone_offset_y, z_cylindrical_bottom), App.Vector(0, 0, -1))
    
    # 將旋流器主體融合入整體流體網格
    fluid_domain = fluid_domain.fuse(cylindrical_section).fuse(conical_section)

    # ==========================================
    # 6. 建立溢流管 BUILD VORTEX FINDER (The Overflow pipe)
    # ==========================================
    # 乾淨水會由呢條管向上排出，而家佢獨立於旋流器正上方
    overflow_outer_r = 20.0
    overflow_inner_r = 16.0  
    overflow_length = 80.0
    
    z_vf_bottom = z_cyclone_top - 40.0 # 插入旋流室內部 40mm
    vf_outer = Part.makeCylinder(overflow_outer_r, overflow_length, App.Vector(cyclone_offset_x, cyclone_offset_y, z_vf_bottom), App.Vector(0, 0, 1))
    vf_inner = Part.makeCylinder(overflow_inner_r, overflow_length, App.Vector(cyclone_offset_x, cyclone_offset_y, z_vf_bottom), App.Vector(0, 0, 1))
    overflow_wall_hardware = vf_outer.cut(vf_inner)
    
    # 喺流體實體入面挖走呢條實體喉管嘅空間
    fluid_domain = fluid_domain.cut(overflow_wall_hardware)

    # ==========================================
    # 7. 清理網格及匯出 CLEANUP & EXPORT
    # ==========================================
    fluid_domain = fluid_domain.removeSplitter()

    cfd_part = doc.addObject("Part::Feature", "FluidVolume")
    cfd_part.Shape = fluid_domain
    cfd_part.Label = "Fluid_Domain_Harvesting_Ready"

    doc.recompute()
    
    try:
        import FreeCADGui
        FreeCADGui.SendMsgToActiveView("ViewFit")
        FreeCADGui.activeDocument().activeView().viewAxometric()
    except Exception as e:
        pass

create_full_system_cfd_domain()
print("Harvesting-Ready Full System Model successfully generated!")