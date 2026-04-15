class_mapping = {
    "macaroni1": "macaroni",
    "macaroni2": "macaroni",
    "pcb1": "printed circuit board",
    "pcb2": "printed circuit board",
    "pcb3": "printed circuit board",
    "pcb4": "printed circuit board",
    "pipe_fryum": "pipe fryum",
    "chewinggum": "chewing gum",
    "metal_nut": "metal nut"
}



state_anomaly = ["damaged {}",
                 "flawed {}",
                 "abnormal {}",
                 "imperfect {}",
                 "blemished {}",
                 "{} with flaw",
                 "{} with defect",
                 "{} with damage"]

abnormal_state0 = ['damaged {}', 'broken {}', '{} with flaw', '{} with defect', '{} with damage']

#
class_state_abnormal_refined = {
    'bottle': ['{} with large breakage', '{} with small breakage', '{} with contamination'],
    'toothbrush': ['{} with defect', '{} with anomaly'],
    'carpet': ['{} with hole', '{} with color stain', '{} with metal contamination', '{} with thread residue', '{} with thread', '{} with cut'],
    'hazelnut': ['{} with crack', '{} with cut', '{} with hole', '{} with print'],
    'leather': ['{} with color stain', '{} with cut', '{} with fold', '{} with glue', '{} with poke'],
    'cable': ['{} with bent wire', '{} with missing part', '{} with missing wire', '{} with cut', '{} with poke'],
    'capsule': ['{} with crack', '{} with faulty imprint', '{} with poke', '{} with scratch', '{} squeezed with compression'],
    'grid': ['{} with breakage',  '{} with thread residue', '{} with thread', '{} with metal contamination', '{} with glue', '{} with a bent shape'],
    'pill': ['{} with color stain', '{} with contamination', '{} with crack', '{} with faulty imprint', '{} with scratch', '{} with abnormal type'],
    'transistor': ['{} with bent lead', '{} with cut lead', '{} with damage', '{} with misplaced transistor'],
    'metal_nut': ['{} with a bent shape ', '{} with color stain', '{} with a flipped orientation', '{} with scratch'],
    'screw': ['{} with manipulated front',  '{} with scratch neck', '{} with scratch head'],
    'zipper': ['{} with broken teeth', '{} with fabric border', '{} with defect fabric', '{} with broken fabric', '{} with split teeth', '{} with squeezed teeth'],
    'tile': ['{} with crack', '{} with glue strip', '{} with gray stroke', '{} with oil', '{} with rough surface'],
    'wood': ['{} with color stain', '{} with hole', '{} with scratch', '{} with liquid'],

    'candle': ['{} with melded wax', '{} with foreign particals', '{} with extra wax', '{} with chunk of wax missing', '{} with weird candle wick', '{} with damaged corner of packaging', '{} with different colour spot'],
    'capsules': ['{} with scratch', '{} with discolor', '{} with misshape', '{} with leak', '{} with bubble'],
    # 'capsules': [],
    'cashew': ['{} with breakage', '{} with small scratches', '{} with burnt', '{} with stuck together', '{} with spot'],
    'chewinggum': ['{} with corner missing', '{} with scratches', '{} with chunk of gum missing', '{} with colour spot', '{} with cracks'],
    'fryum': ['{} with breakage', '{} with scratches', '{} with burnt', '{} with colour spot', '{} with fryum stuck together', '{} with colour spot'],
    'macaroni1': ['{} with color spot', '{} with small chip around edge', '{} with small scratches', '{} with breakage', '{} with cracks'],
    'macaroni2': ['{} with color spot', '{} with small chip around edge', '{} with small scratches', '{} with breakage', '{} with cracks'],
    'pcb1': ['{} with bent', '{} with scratch', '{} with missing', '{} with melt'],
    'pcb2': ['{} with bent', '{} with scratch', '{} with missing', '{} with melt'],
    'pcb3': ['{} with bent', '{} with scratch', '{} with missing', '{} with melt'],
    'pcb4': ['{} with scratch', '{} with extra', '{} with missing', '{} with wrong place', '{} with damage', '{} with burnt', '{} with dirt'],
    'pipe_fryum': ['{} with breakage', '{} with small scratches', '{} with burnt', '{} with stuck together', '{} with colour spot', '{} with cracks']}


#
# bent, frayed, misaligned, excessive stiffness, corroded, detaches, loose, warped

class_state_abnormal_refined_filo = {
    'bottle': ['{} with large breakage', '{} with small breakage', '{} with contamination'
               '{} with cracked large', '{} with cracked small', '{} with dented large', '{} with dented small', 
               '{} with leaking', '{} with discolored', '{} with deformed', '{} with missing cap',
               '{} with excessive condensation', '{} with unusual odor'
              ],
    'toothbrush': ['{} with defect', '{} with anomaly', '{} with loose bristles', '{} with uneven bristle distribution', 
                   '{} with excessive shedding of bristles', '{} with staining on the bristles', 
                   '{} with abrasive texture', '{} with irregularities in the shape'
                  ],
    'carpet': ['{} with hole', '{} with color stain', '{} with metal contamination', '{} with thread residue', '{} with thread', '{} with cut', '{} with discoloration in a specific area', '{} with irregular patch or section with a different texture', '{} with frayed edges or unraveling fibers', '{} with burn mark or scorching'],
    'hazelnut': ['{} with crack', '{} with cut', '{} with hole', 
                 '{} with print', '{} with fungal growth', '{} with unusual discoloration', '{} with rotten or foul odor emanating',
                 '{} with insect infestation', '{} with wetness', '{} with misshapen shell', '{} with unusually thin', '{} with contaminants',
                 '{} with unusual texture'
                ],
    'leather': ['{} with color stain', '{} with cut', '{} with fold', '{} with glue', 
                '{} with poke', '{} with scratches', '{} with discoloration', '{} with creases', 
                '{} with uneven texture', '{} with tears', '{} with brittleness', 
                '{} with damage', '{} with seams', '{} with heat damage', '{} with mold'
               ],
    'cable': ['{} with bent wire', '{} with missing part', '{} with missing wire',
              '{} with cut', '{} with poke', '{} with twisted, knotted cable strands',
              '{} with detached connectors', '{} with excessive stretching',
              '{} with dents', '{} with corrosion', '{} with scorching along the cable',
              '{} with exposed conductive material'
             ],
    'capsule': ['{} with crack', '{} with faulty imprint', '{} with poke', 
                '{} with scratch', '{} squeezed with compression',
                '{} with irregular shape', '{} with discoloration coloring',
                '{} with crinkled', '{} with uneven seam', '{} with condensation inside the capsule',
                '{} with foreign particles', '{} with unusually soft or hard'
               ],
    'grid': ['{} with breakage',  '{} with thread residue', 
             '{} with thread', '{} with metal contamination', 
             '{} with glue', '{} with a bent shape', '{} with crooked', 
             '{} with cracks', '{} with excessive gaps', '{} with discoloration', 
             '{} with deformation', '{} with missing', '{} with inconsistent spacing between grid elements', 
             '{} with corrosion', '{} with visible signs', '{} with chipping'
            ],
    'pill': ['{} with color stain', '{} with contamination', '{} with crack', 
             '{} with faulty imprint', '{} with scratch', '{} with abnormal type',
             '{} with irregular shape', '{} with crumbling texture', '{} with excessive powder',
             '{} with uneven coating', '{} with presence of air bubbles', '{} with disintegration', '{} with abnormal specks'
             ],
    'transistor': ['{} with bent lead', '{} with cut lead', '{} with damage', '{} with misplaced transistor',
                   '{} with burn marks', '{} with detached leads', '{} with signs of corrosion', '{} with irregularities in the shape',
                  '{} with presence of cracks or fractures', '{} with signs of physical trauma', '{} with irregularities in the surface texture' 
                  ],
    'metal_nut': ['{} with a bent shape ', '{} with color stain', 
                  '{} with a flipped orientation', '{} with scratch',
                  '{} with cracks', '{} with irregular threading', 
                  '{} with corrosion', '{} with missing', '{} with distortion', '{} with signs of discoloration', 
                  '{} with excessive wear on contact surfaces', '{} with inconsistent texture'
                 ],
    'screw': ['{} with manipulated front',  '{} with scratch neck', '{} with scratch head',
              '{} with rust on the surface', '{} with bent', '{} with damaged threads',
              '{} with stripped threads', '{} with deformed top', '{} with coating damage',
              '{} with uneven grooves', '{} with inconsistent size' 
             ],
    'zipper': ['{} with broken teeth', '{} with fabric border', 
               '{} with defect fabric', '{} with broken fabric', 
               '{} with split teeth', '{} with squeezed teeth'
               '{} with bent', '{} with frayed', '{} with misaligned',
               '{} with excessive stiffness', '{} with corroded', '{} with detaches', '{} with loose', '{} with warped'
               ],
    'tile': ['{} with crack', '{} with glue strip', '{} with gray stroke', 
             '{} with oil', '{} with rough surface', '{} with chipped', '{} with irregularities', '{} with discoloration',
            '{} with efflorescence', '{} with warping', '{} with missing', 
            '{} with depressions', '{} with lippage', '{} with fungus', '{} with damage'
            ],
    'wood': ['{} with color stain', '{} with hole', 
             '{} with scratch', '{} with liquid', '{} with knots', '{} with warping',
                '{} with cracks along the grain', '{} with mold growth on the surface',
                '{} with staining from water damage', '{} with wood rot', '{} with woodworm holes',
                '{} with rough patches', '{} with protruding knots'
            ],

    'candle': ['{} with melded wax', '{} with foreign particals', '{} with extra wax', '{} with chunk of wax missing', '{} with weird candle wick', '{} with damaged corner of packaging', '{} with different colour spot'],
    'capsules': ['{} with scratch', '{} with discolor', '{} with misshape', '{} with leak', '{} with bubble'],
    # 'capsules': [],
    'cashew': ['{} with breakage', '{} with small scratches', '{} with burnt', '{} with stuck together', '{} with spot'],
    'chewinggum': ['{} with corner missing', '{} with scratches', '{} with chunk of gum missing', '{} with colour spot', '{} with cracks'],
    'fryum': ['{} with breakage', '{} with scratches', '{} with burnt', '{} with colour spot', '{} with fryum stuck together', '{} with colour spot'],
    'macaroni1': ['{} with color spot', '{} with small chip around edge', '{} with small scratches', '{} with breakage', '{} with cracks'],
    'macaroni2': ['{} with color spot', '{} with small chip around edge', '{} with small scratches', '{} with breakage', '{} with cracks'],
    'pcb1': ['{} with bent', '{} with scratch', '{} with missing', '{} with melt'],
    'pcb2': ['{} with bent', '{} with scratch', '{} with missing', '{} with melt'],
    'pcb3': ['{} with bent', '{} with scratch', '{} with missing', '{} with melt'],
    'pcb4': ['{} with scratch', '{} with extra', '{} with missing', '{} with wrong place', '{} with damage', '{} with burnt', '{} with dirt'],
    'pipe_fryum': ['{} with breakage', '{} with small scratches', '{} with burnt', '{} with stuck together', '{} with colour spot', '{} with cracks']}



#对于存在异常的bottle的Level_3会存在一定的变化，如texture，变得不再光滑，因此需要替换成可学习的
#实际做法就是从caption里KMP texture的字段，然后直接进行替换为可学习的tensor.



#这里面放所有类别的细粒度描述，做一个list来映射对应的类别和索引
fine_grained_normal_prompts_old = [
    {
    "Level_1": [
        {
            "foreground": "bottle",
            "background": "pure white"
        }
    ],
    "Level_2": [
        {
            "entity": ["bottle"],
            "number": ["1"],
            "location": ["center"]
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["black"],
            "texture": ["smooth"],
            "shape": ["cylindrical"]
        }
    ],
    "caption": "The image shows a single black cylindrical bottle positioned centrally against a pure white background. The bottle has a smooth texture and is viewed from the top, highlighting its circular opening."
    },
    {
    "Level_1": [
        {
            "foreground": "cable",
            "background": "pure black"
        }
    ],
    "Level_2": [
        {
            "entity": ["yellow wire", "blue wire", "brown wire"],
            "number": ["1", "1", "1"],
            "location": ["top right", "bottom left", "bottom right"]
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None"],
            "color": ["yellow", "blue", "brown"],
            "texture": ["smooth", "smooth", "smooth"],
            "shape": ["cylindrical", "cylindrical", "cylindrical"]
        }
    ],
    "caption": "The image shows a cross-section of a cable with three wires inside. The wires are colored yellow, blue, and brown. The yellow wire is located at the top right, the blue wire at the bottom left, and the brown wire at the bottom right. Each wire has a smooth texture and a cylindrical shape. The background of the image is pure black, highlighting the cable and its internal wires."
    },
    {
    "Level_1": [
        {
            "foreground": "capsule",
            "background": "white"
        }
    ],
    "Level_2": [
        {
            "entity": ["capsule"],
            "number": ["1"],
            "location": ["center"]
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["black", "orange"],
            "texture": ["smooth"],
            "shape": ["cylindrical"]
        }
    ],
    "caption": "A single two-toned capsule with a black and orange exterior is centered on a white background. The black half of the capsule features a logo, while the orange half has '500' printed on it. The surface of the capsule appears smooth, and its shape is cylindrical, typical for oral medication capsules."
    },
    {
    "Level_1": [
        {
            "foreground": "carpet",
            "background": "none"
        },
    ],
    "Level_2": [
        {
            "entity": ["woven fibers"],
            "number": ["multiple"],
            "location": ["throughout"]
        },
    ],
    "Level_3": [
        {
            "direction": ["interlaced"],
            "color": ["gray", "black", "white"],
            "texture": ["textured"],
            "shape": ["rectangular"]
        },
    ],
    "caption": "This image showcases a close-up view of a carpet with interlaced woven fibers. The fibers are predominantly gray, with hints of black and white, creating a textured appearance. The shape of the visible carpet area is rectangular, and the intricate weaving pattern is consistent throughout the image, indicating a uniform manufacturing process."
    },
    {
    "Level_1": [
        {
            "foreground": "grid",
            "background": "none"
        }
    ],
    "Level_2": [
        {
            "entity": ["diamond-shaped grid pattern"],
            "number": ["multiple"],
            "location": ["throughout"]
        }
    ],
    "Level_3": [
        {
            "direction": ["uniform"],
            "color": ["monochrome"],
            "texture": ["textured"],
            "shape": ["diamond-shaped"]
        }
    ],
    "caption": "The image displays a uniform, diamond-shaped grid pattern that covers the entire frame. The grid is monochrome, featuring a textured surface with multiple diamond shapes repeated throughout."
    },
    {
    "Level_1": [
        {
            "foreground": "hazelnut",
            "background": "pure black"
        },
    ],
    "Level_2": [
        {
            "entity": ["hazelnut"],
            "number": ["1"],
            "location": ["center"],
        },
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["brown"],
            "texture": ["smooth"],
            "shape": ["spherical"]
        },
    ],
    "caption": "A single brown hazelnut with a smooth texture and a spherical shape is centered against a pure black background."
    },
    {
    "Level_1": [
        {
            "foreground": "leather",
            "background": "uniform"
        },
    ],
    "Level_2": [
        {
            "entity": ["leather texture"],
            "number": ["1"],
            "location": ["center"]
        },
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["brown"],
            "texture": ["grained"],
            "shape": ["irregular"]
        },
    ],
    "caption": "The image displays a single, uniform piece of brown leather with a grained texture occupying the entire view. The leather has an irregular shape and is centered in the image, set against a uniform background that matches the leather itself."
    },
    {
    "Level_1": [
        {
            "foreground": "metal nut",
            "background": "pure black"
        },
    ],
    "Level_2": [
        {
            "entity": ["metal nut"],
            "number": ["1"],
            "location": ["center"],
        },
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["silver"],
            "texture": ["textured"],
            "shape": ["hexagonal"]
        },
    ],
    "caption": "A single silver metal nut with a textured surface is centered against a pure black background. The nut has a hexagonal outer shape and a circular inner hole."
    },
    {
    "Level_1": [
        {
            "foreground": "pill",
            "background": "pure black"
        },
    ],
    "Level_2": [
        {
            "entity": ["pill"],
            "number": ["1"],
            "location": ["center"],
        },
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["white with red specks"],
            "texture": ["smooth"],
            "shape": ["oval"]
        },
    ],
    "caption": "A single oval-shaped pill with a smooth texture and white color, speckled with red spots, prominently embossed with the letters 'FF' in the center, set against a pure black background."
    },
    {
    "Level_1": [
        {
            "foreground": "screw",
            "background": "light grey"
        }
    ],
    "Level_2": [
        {
            "entity": ["screw"],
            "number": ["1"],
            "location": ["center"]
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["metallic grey"],
            "texture": ["threaded"],
            "shape": ["cylindrical"]
        }
    ],
    "caption": "A single metallic grey screw with a threaded texture and cylindrical shape is centered against a light grey background."
    },
    {
    "Level_1": [
        {
            "foreground": "tile",
            "background": "consistent pattern"
        }
    ],
    "Level_2": [
        {
            "entity": ["speckles"],
            "number": ["multiple"],
            "location": ["throughout"]
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["grey", "black"],
            "texture": ["granular"],
            "shape": ["irregular"]
        }
    ],
    "caption": "This is an image of a tile with a consistent speckled pattern throughout. The tile features multiple grey and black speckles of irregular shape and granular texture, distributed evenly across the surface."
    },
    {
    "Level_1": [
        {
            "foreground": "toothbrush",
            "background": "pure black"
        },
    ],
    "Level_2": [
        {
            "entity": ["bristle clusters", "toothbrush handle"],
            "number": ["many", "1"],
            "location": ["center", "bottom"]
        },
    ],
    "Level_3": [
        {
            "direction": ["upward", "None"],
            "color": ["blue and white", "white"],
            "texture": ["bristled", "smooth"],
            "shape": ["rounded", "elongated"]
        },
    ],
    "caption": "A close-up image of a toothbrush with a white handle, featuring many clusters of bristles in the center, arranged in an orderly fashion. The bristles are a combination of blue and white, with the blue bristles appearing to be at the tips. The bristles are oriented upward, indicating the brushing surface of the toothbrush. The handle is smooth and elongated, contrasting with the textured bristles. The entire toothbrush is set against a pure black background, highlighting the details of the bristles and the cleanliness of the handle."
    },
    {
    "Level_1": [
        {
            "foreground": "transistor",
            "background": "brown circuit board with circular patterns"
        }
    ],
    "Level_2": [
        {
            "entity": ["transistor body", "transistor legs", "circular patterns", "circuit board"],
            "number": ["1", "3", "multiple", "1"],
            "location": ["center", "bottom", "surrounding", "entire image"]
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "downward", "None", "None"],
            "color": ["black", "silver", "dark brown and copper", "brown"],
            "texture": ["smooth", "metallic", "smooth", "smooth"],
            "shape": ["rectangular", "straight and bent", "circular", "rectangular"]
        }
    ],
    "caption": "The image showcases a black transistor with three metallic legs extending downward, mounted on a brown circuit board featuring multiple dark brown and copper circular patterns. The transistor body is rectangular and smooth, while the legs have a metallic texture and are straight with some bending at the ends. The circuit board fills the entire image and has a smooth texture with a consistent pattern of circular shapes."
    },
    {
    "Level_1": [
        {
            "foreground": "wood",
            "background": "none"
        }
    ],
    "Level_2": [
        {
            "entity": ["wood grain"],
            "number": ["1"],
            "location": ["center"]
        }
    ],
    "Level_3": [
        {
            "direction": ["vertical"],
            "color": ["various shades of brown"],
            "texture": ["smooth"],
            "shape": ["flat"]
        }
    ],
    "caption": "The image displays a single, smooth wooden surface with vertical wood grain patterns in various shades of brown, covering the entire view without any distinct background."
    },
    {
    "Level_1": [
        {
            "foreground": "zipper",
            "background": "textured fabric"
        }
    ],
    "Level_2": [
        {
            "entity": ["zipper teeth", "zipper tape"],
            "number": ["multiple", "2"],
            "location": ["center", "both sides"]
        }
    ],
    "Level_3": [
        {
            "direction": ["vertical", "vertical"],
            "color": ["dark gray", "black"],
            "texture": ["smooth", "textured"],
            "shape": ["interlocking", "flat"]
        }
    ],
    "caption": "A close-up view of a zipper with multiple dark gray interlocking teeth aligned vertically in the center, flanked by two flat black zipper tapes with a textured surface on both sides."
    },
    {
    "Level_1": [
        {
            "foreground": "candles",
            "background": "dark"
        }
    ],
    "Level_2": [
        {
            "entity": ["candle", "candle", "candle", "candle"],
            "number": ["1", "1", "1", "1"],
            "location": ["top left", "top right", "bottom left", "bottom right"]
        }
    ],
    "Level_3": [
        {
            "direction": ["upward", "upward", "upward", "upward"],
            "color": ["white", "white", "white", "white"],
            "texture": ["smooth", "smooth", "smooth", "smooth"],
            "shape": ["cylindrical", "cylindrical", "cylindrical", "cylindrical"]
        }
    ],
    "caption": "Four white cylindrical candles with smooth texture are arranged in a two-by-two grid against a dark background. Each candle is positioned with the wick facing upward, located at the top left, top right, bottom left, and bottom right respectively."
    },
    {
    "Level_1": [
        {
            "foreground": "capsules",
            "background": "gray textured"
        }
    ],
    "Level_2": [
        {
            "entity": ["capsule"],
            "number": ["multiple"],
            "location": ["scattered"]
        }
    ],
    "Level_3": [
        {
            "direction": ["various"],
            "color": ["green"],
            "texture": ["smooth"],
            "shape": ["cylindrical"]
        }
    ],
    "caption": "Multiple green, smooth, cylindrical capsules are scattered across a gray textured background. The capsules are oriented in various directions and have a consistent green color, suggesting they are likely identical in content."
    },
    {
    "Level_1": [
        {
            "foreground": "cashew",
            "background": "dark textured"
        },
    ],
    "Level_2": [
        {
            "entity": ["cashew"],
            "number": ["1"],
            "location": ["center"],
        },
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["beige"],
            "texture": ["smooth"],
            "shape": ["kidney-shaped"]
        },
    ],
    "caption": "A single beige, smooth, kidney-shaped cashew is centered on a dark textured background."
    },
    {
    "Level_1": [
        {
            "foreground": "chewing gum",
            "background": "textured black surface"
        },
    ],
    "Level_2": [
        {
            "entity": ["chewing gum"],
            "number": ["1"],
            "location": ["center"],
        },
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["white"],
            "texture": ["smooth"],
            "shape": ["rectangular"]
        },
    ],
    "caption": "A single piece of white chewing gum is centered on a textured black surface with a smooth texture and rectangular shape."
    },
    {
    "Level_1": [
        {
            "foreground": "fryum",
            "background": "green textured"
        }
    ],
    "Level_2": [
        {
            "entity": ["fryum"],
            "number": ["1"],
            "location": ["center"]
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["light orange"],
            "texture": ["smooth"],
            "shape": ["circular with radial spokes"]
        }
    ],
    "caption": "A single light orange fryum with a smooth texture and a circular shape featuring radial spokes, centered against a green textured background."
    },
    {
    "Level_1": [
        {
            "foreground": "macaroni",
            "background": "green"
        }
    ],
    "Level_2": [
        {
            "entity": ["macaroni", "macaroni", "macaroni", "macaroni"],
            "number": ["1", "1", "1", "1"],
            "location": ["top left", "top right", "bottom left", "bottom right"]
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None", "None"],
            "color": ["yellow", "yellow", "yellow", "yellow"],
            "texture": ["smooth", "smooth", "smooth", "smooth"],
            "shape": ["crescent", "crescent", "crescent", "crescent"]
        }
    ],
    "caption": "Four pieces of smooth, yellow crescent-shaped macaroni are neatly arranged against a textured green background, with two pieces positioned on the top and two on the bottom."
    },
    {
    "Level_1": [
        {
            "foreground": "macaroni",
            "background": "green textured"
        },
    ],
    "Level_2": [
        {
            "entity": ["macaroni", "macaroni", "macaroni", "macaroni"],
            "number": ["1", "1", "1", "1"],
            "location": ["top left", "top right", "bottom left", "bottom right"],
        },
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None", "None"],
            "color": ["yellow", "yellow", "yellow", "yellow"],
            "texture": ["smooth", "smooth", "smooth", "smooth"],
            "shape": ["curved tube", "curved tube", "curved tube", "curved tube"]
        },
    ],
    "caption": "Four pieces of smooth, yellow macaroni are evenly spaced on a green textured background, with each piece located at the top left, top right, bottom left, and bottom right of the image."
    },
    {
    "Level_1": [
        {
            "foreground": "printed circuit board",
            "background": "pure black"
        }
    ],
    "Level_2": [
        {
            "entity": ["ultrasonic sensors", "pins", "capacitor"],
            "number": ["2", "4", "1"],
            "location": ["left and right", "top center", "center bottom"]
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "vertical", "horizontal"],
            "color": ["silver", "silver", "silver"],
            "texture": ["smooth", "smooth", "smooth"],
            "shape": ["circular", "rectangular", "rectangular"]
        }
    ],
    "caption": "The image shows a printed circuit board (PCB) with a pure black background. The PCB features two ultrasonic sensors located on the left and right sides, four vertical pins at the top center, and a single capacitor positioned at the center bottom. The ultrasonic sensors are silver in color, smooth in texture, and circular in shape. The pins are also silver, smooth, and rectangular. The capacitor is silver, smooth, and rectangular."
    },
    {
    "Level_1": [
        {
            "foreground": "printed circuit board",
            "background": "pure black"
        }
    ],
    "Level_2": [
        {
            "entity": ["integrated circuit", "resistor", "capacitor", "pin header"],
            "number": ["3", "multiple", "multiple", "1"],
            "location": ["left", "center", "center", "top"]
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None", "vertical"],
            "color": ["black", "blue", "blue", "silver"],
            "texture": ["smooth", "smooth", "smooth", "smooth"],
            "shape": ["rectangular", "rectangular", "rectangular", "rectangular"]
        }
    ],
    "caption": "The image displays a printed circuit board (PCB) against a pure black background. The PCB features three integrated circuits positioned on the left and center. Multiple resistors and capacitors are also present, mainly located in the center of the board. At the top of the PCB, there is a vertical pin header. The components are primarily black, blue, and silver in color, with smooth and rectangular shapes."
    },
    {
    "Level_1": [
        {
            "foreground": "printed circuit board",
            "background": "green"
        }
    ],
    "Level_2": [
        {
            "entity": ["resistors", "capacitors", "LED", "pins", "potentiometer"],
            "number": ["4", "2", "2", "3", "1"],
            "location": ["top right", "top left", "right", "left", "center"]
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None", "None", "None"],
            "color": ["black", "black", "transparent and black", "silver", "blue"],
            "texture": ["smooth", "smooth", "smooth", "smooth", "smooth"],
            "shape": ["cylindrical", "rectangular", "cylindrical", "cylindrical", "rectangular"]
        }
    ],
    "caption": "The image displays a printed circuit board (PCB) against a green background. The PCB features several components: four black cylindrical resistors located at the top right, two black rectangular capacitors at the top left, two LEDs (one transparent and one black) on the right, three silver cylindrical pins on the left, and a blue rectangular potentiometer in the center. All components have a smooth texture."
    },
    {
    "Level_1": [
        {
            "foreground": "printed circuit board",
            "background": "pure black"
        }
    ],
    "Level_2": [
        {
            "entity": ["micro USB port", "resistor", "capacitor", "integrated circuit", "solder points"],
            "number": ["1", "2", "2", "1", "4"],
            "location": ["left", "top center", "center", "right center", "corners"]
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None", "None", "None"],
            "color": ["silver", "black", "yellow", "black", "silver"],
            "texture": ["smooth", "smooth", "smooth", "smooth", "smooth"],
            "shape": ["rectangular", "rectangular", "cylindrical", "rectangular", "circular"]
        }
    ],
    "caption": "The image displays a printed circuit board (PCB) against a pure black background. The PCB features several components: a micro USB port located on the left, two resistors positioned at the top center, two capacitors in the center, an integrated circuit at the right center, and four solder points at the corners. The components exhibit various colors, including silver for the micro USB port and solder points, black for the resistors and integrated circuit, and yellow for the capacitors. All components have a smooth texture, with the micro USB port and integrated circuit being rectangular, the capacitors cylindrical, and the solder points circular."
    },
    {
    "Level_1": [
        {
            "foreground": "pipe fryum",
            "background": "pure black"
        }
    ],
    "Level_2": [
        {
            "entity": ["pipe fryum"],
            "number": ["1"],
            "location": ["center"]
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["light beige"],
            "texture": ["rough"],
            "shape": ["cylindrical"]
        }
    ],
    "caption": "The image features a single pipe fryum positioned at the center against a pure black background. The fryum is light beige in color, has a rough texture, and is cylindrical in shape."
    }
]

#这里面放所有类别的细粒度描述，做一个list来映射对应的类别和索引
fine_grained_normal_prompts_v2 = [
    {
    "Level_1": [
        {
            "foreground": "bottle",
            "background": "pure white"
        }
    ],
    "Level_2": [
        {
            "entity": ["bottle"],
            "number": ["1"],
            "location": ["center"],
            "entity_caption": ["A single bottle is positioned at the center of the image, viewed from the top."],
            "relation": "The bottle is centrally located in the image."
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["black"],
            "texture": ["smooth"],
            "shape": ["circular"]
        }
    ],
    "caption": "The image shows a single black circular bottle positioned centrally against a pure white background. The bottle has a smooth texture and is viewed from the top, highlighting its circular opening."
    },
    {
    "Level_1": [
        {
            "foreground": "cable",
            "background": "gray textured surface"
        }
    ],
    "Level_2": [
        {
            "entity": ["yellow wire", "blue wire", "brown wire"],
            "number": ["1", "1", "1"],
            "location": ["top right", "bottom left", "bottom right"],
            "entity_caption": [
                "A yellow wire with copper strands at the top right.",
                "A blue wire with copper strands at the bottom left.",
                "A brown wire with copper strands at the bottom right."
            ],
            "relation": "The three wires are bundled together within a circular cable sheath, with the yellow wire positioned at the top right, the blue wire at the bottom left, and the brown wire at the bottom right."
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None"],
            "color": ["yellow", "blue", "brown"],
            "texture": ["smooth", "smooth", "smooth"],
            "shape": ["cylindrical", "cylindrical", "cylindrical"]
        }
    ],
    "caption": "The image shows a close-up view of a cable with three distinct wires inside a circular sheath. The wires are colored yellow, blue, and brown, and are positioned at the top right, bottom left, and bottom right respectively. Each wire has a smooth texture and a cylindrical shape, and the cable is set against a gray textured surface."
    },
    {
    "Level_1": [
        {
            "foreground": "capsule",
            "background": "white"
        }
    ],
    "Level_2": [
        {
            "entity": ["capsule"],
            "number": ["1"],
            "location": ["center"],
            "entity_caption": ["A single capsule is placed in the center of the image. The capsule is divided into two halves, with one half being black and the other half being orange. The black half has the text 'actavis' printed on it, while the orange half has the number '500' printed on it."],
            "relation": "The capsule is centrally placed against a pure white background."
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["black", "orange"],
            "texture": ["smooth"],
            "shape": ["cylindrical"]
        }
    ],
    "caption": "The image features a single capsule placed horizontally in the center against a pure white background. The capsule is cylindrical in shape with a smooth texture. It has two distinct colors: the left half is black with the text 'actavis' printed on it, and the right half is orange with the number '500' printed on it."
    },
    {
    "Level_1": [
        {
            "foreground": "carpet",
            "background": "none"
        },
    ],
    "Level_2": [
        {
            "entity": ["woven fibers"],
            "number": ["multiple"],
            "location": ["throughout"],
            "entity_caption": ["A close-up view of a carpet with multiple woven fibers."],
            "relation": "The woven fibers are uniformly distributed throughout the image, creating a consistent texture."
        },
    ],
    "Level_3": [
        {
            "direction": ["interlaced"],
            "color": ["gray", "black", "white"],
            "texture": ["textured"],
            "shape": ["rectangular"]
        },
    ],
    "caption": "This image showcases a close-up view of a carpet with interlaced woven fibers. The fibers are predominantly gray, with hints of black and white, creating a textured appearance. The shape of the visible carpet area is rectangular, and the intricate weaving pattern is consistent throughout the image, indicating a uniform manufacturing process."
    },
    {
    "Level_1": [
        {
            "foreground": "grid",
            "background": "gray"
        }
    ],
    "Level_2": [
        {
            "entity": ["diamond-shaped grid pattern"],
            "number": ["multiple"],
            "location": ["center"],
            "entity_caption": ["A repeating diamond-shaped grid pattern."],
            "relation": "The grid is centrally located and spans the entire image."
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["black"],
            "texture": ["smooth"],
            "shape": ["diamond-shaped"]
        }
    ],
    "caption": "The image features a centrally located black grid with a diamond shape pattern against a gray background. The grid spans the entire image and has a smooth texture."
    },
    {
    "Level_1": [
        {
            "foreground": "hazelnut",
            "background": "pure black"
        },
    ],
    "Level_2": [
        {
            "entity": ["hazelnut"],
            "number": ["1"],
            "location": ["center"],
            "entity_caption": ["A single hazelnut is positioned centrally against a pure black background."],
            "relation": "The hazelnut is centrally located against a pure black background."
        },
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["brown"],
            "texture": ["smooth"],
            "shape": ["spherical"]
        },
    ],
    "caption": "A single brown hazelnut with a smooth texture and a spherical shape is centered against a pure black background."
    },
    {
    "Level_1": [
        {
            "foreground": "leather",
            "background": "none"
        },
    ],
    "Level_2": [
        {
            "entity": ["leather texture"],
            "number": ["1"],
            "location": ["center"],
            "entity_caption": ["A leather texture is prominently displayed in the center of the image."],
            "relation": "The leather texture occupies the entire image, centered within the frame."
        },
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["brown"],
            "texture": ["rough"],
            "shape": ["irregular"]
        },
    ],
    "caption": "The image showcases a piece of brown leather with a rough, irregular texture. The leather occupies the entire image, centered within the frame."
    },
    {
    "Level_1": [
        {
            "foreground": "metal nut",
            "background": "pure black"
        },
    ],
    "Level_2": [
        {
            "entity": ["metal nut"],
            "number": ["1"],
            "location": ["center"],
            "entity_caption": ["A single metal nut is positioned at the center of the image."],
            "relation": "The metal nut is positioned centrally against a pure black background."
        },
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["metallic silver"],
            "texture": ["rough"],
            "shape": ["hexagonal"]
        },
    ],
    "caption": "A single metallic silver metal nut with a rough surface is centered against a pure black background. The nut has a hexagonal outer shape and a circular inner hole."
    },
    {
    "Level_1": [
        {
            "foreground": "pill",
            "background": "pure black"
        },
    ],
    "Level_2": [
        {
            "entity": ["pill"],
            "number": ["1"],
            "location": ["center"],
            "entity_caption": ["A single pill is located at the center of the image."],
            "relation": "The pill is centrally located against a pure black background."
        },
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["white with red specks"],
            "texture": ["smooth"],
            "shape": ["oval"]
        },
    ],
    "caption": "A single oval-shaped pill with a smooth texture and white color, speckled with red spots, prominently embossed with the letters 'FF' in the center, set against a pure black background."
    },
    {
    "Level_1": [
        {
            "foreground": "screw",
            "background": "light grey"
        }
    ],
    "Level_2": [
        {
            "entity": ["screw"],
            "number": ["1"],
            "location": ["center"],
            "entity_caption": ["A single screw is positioned in the center of the image."],
            "relation": "The screw is positioned at the center of the image."
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["metallic grey"],
            "texture": ["smooth and threaded"],
            "shape": ["cylindrical with a pointed tip and flat head"]
        }
    ],
    "caption": "A single metallic gray screw is centered against a light gray background. The screw has a smooth cylindrical body with a threaded section, a pointed tip, and a flat head."
    },
    {
    "Level_1": [
        {
            "foreground": "tile",
            "background": "consistent pattern"
        }
    ],
    "Level_2": [
        {
            "entity": ["speckles"],
            "number": ["multiple"],
            "location": ["throughout"],
            "entity_caption": ["The speckles are scattered across the tile."],
            "relation": "The speckles are evenly distributed across the entire surface of the tile."
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["grey"],
            "texture": ["granular"],
            "shape": ["irregular"]
        }
    ],
    "caption": "The image displays a close-up view of a tile with a granular texture, featuring a multitude of irregularly shaped grey, black, and white speckles that are evenly distributed throughout the surface, creating a consistent pattern."
    },
    {
    "Level_1": [
        {
            "foreground": "toothbrush",
            "background": "pure black"
        },
    ],
    "Level_2": [
        {
            "entity": ["bristle clusters", "toothbrush handle"],
            "number": ["multiple", "1"],
            "location": ["center", "bottom"],
            "entity_caption": ["Multiple bristle clusters on the toothbrush handle", "The handle of the toothbrush"],
            "relation": "The bristle clusters are mounted on the head of the toothbrush handle."
        },
    ],
    "Level_3": [
        {
            "direction": ["upward", "None"],
            "color": ["blue and white", "white"],
            "texture": ["bristled", "smooth"],
            "shape": ["rounded", "elongated"]
        },
    ],
    "caption": "A close-up image of a toothbrush with a white handle. The head of the toothbrush features many clusters of bristles, with a mix of blue and white colors. The bristles are arranged in a pattern and are oriented upward, indicating the brushing surface. The handle appears smooth and elongated, contrasting with the textured bristles. The entire toothbrush is set against a pure black background, highlighting its details."
    },
    {
    "Level_1": [
        {
            "foreground": "transistor",
            "background": "brown circuit board with circular holes"
        }
    ],
    "Level_2": [
        {
            "entity": ["transistor body", "transistor legs", "circuit board", "circular holes"],
            "number": ["1", "3", "1", "multiple"],
            "location": ["center", "bottom", "entire image", "evenly distributed"],
            "entity_caption": [
                "A black transistor body", 
                "Three silver-colored transistor legs connecting the transistor to the board", 
                "A brown circuit board with a pattern of holes", 
                "An array of circular holes on the circuit board"
            ],
            "relation": "The transistor is mounted on the circuit board, with its legs inserted through the holes."
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "downward", "None", "None"],
            "color": ["black", "silver", "dark brown and copper", "brown"],
            "texture": ["smooth", "metallic", "smooth", "smooth"],
            "shape": ["rectangular", "straight and bent", "circular", "rectangular"]
        }
    ],
    "caption": "A black, smooth-textured transistor with three metallic legs is centrally mounted on a brown circuit board featuring multiple evenly distributed dark brown circular holes. The legs of the transistor are inserted downward through the holes of the circuit board."
    },
    {
    "Level_1": [
        {
            "foreground": "wood",
            "background": "none"
        }
    ],
    "Level_2": [
        {
            "entity": ["wood grain pattern"],
            "number": ["1"],
            "location": ["throughout"],
            "entity_caption": ["A close-up view of a wood grain pattern"],
            "relation": "The wood grain pattern is consistent and covers the entire image."
        }
    ],
    "Level_3": [
        {
            "direction": ["vertical"],
            "color": ["various shades of brown"],
            "texture": ["smooth"],
            "shape": ["flat"]
        }
    ],
    "caption": "The image displays a vertical wood grain pattern with various shades of brown colors, indicating a smooth texture and elongated shapes throughout the surface."
    },
    {
    "Level_1": [
        {
            "foreground": "zipper",
            "background": "textured fabric"
        }
    ],
    "Level_2": [
        {
            "entity": ["zipper teeth", "zipper tape"],
            "number": ["multiple", "2"],
            "location": ["center", "both sides"],
            "entity_caption": ["The metallic zipper teeth are interlocked in the center", "The fabric zipper tapes are running parallel on both sides of the zipper teeth"],
            "relation": "The zipper teeth are aligned in the center, flanked by the zipper tape on both sides."
        }
    ],
    "Level_3": [
        {
            "direction": ["vertical", "vertical"],
            "color": ["black", "black"],
            "texture": ["smooth", "rough"],
            "shape": ["interlocking", "flat"]
        }
    ],
    "caption": "A close-up view of a zipper with multiple dark gray interlocking teeth aligned vertically in the center, flanked by two flat black zipper tapes with a textured surface on both sides."
    },
    {
    "Level_1": [
        {
            "foreground": "candles",
            "background": "dark"
        }
    ],
    "Level_2": [
        {
            "entity": ["candle", "candle", "candle", "candle"],
            "number": ["1", "1", "1", "1"],
            "location": ["top left", "top right", "bottom left", "bottom right"],
            "entity_caption": [
                "A single unlit candle with a wick visible on the top left", 
                "A single unlit candle with a wick visible on the top right", 
                "A single unlit candle with a wick visible on the bottom left", 
                "A single unlit candle with a wick visible on the bottom right"
            ],
            "relation": "The candles are arranged in a 2x2 grid pattern."
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None", "None"],
            "color": ["white", "white", "white", "white"],
            "texture": ["smooth", "smooth", "smooth", "smooth"],
            "shape": ["circular", "circular", "circular", "circular"]
        }
    ],
    "caption": "The image displays four white, smooth, circular candles arranged in a 2x2 grid pattern against a black background. Each candle is positioned in one of the four quadrants: top-left, top-right, bottom-left, and bottom-right."
    },
    {
    "Level_1": [
        {
            "foreground": "capsules",
            "background": "gray textured surface"
        }
    ],
    "Level_2": [
        {
            "entity": ["capsule"],
            "number": ["20"],
            "location": ["scattered"],
            "entity_caption": ["green translucent capsules on a surface"],
            "relation": "The capsules are scattered randomly across the gray textured surface."
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["green"],
            "texture": ["smooth"],
            "shape": ["oval"]
        }
    ],
    "caption": "The image displays 20 green capsules scattered randomly on a gray textured surface. Each capsule is smooth and oval-shaped."
    },
    {
    "Level_1": [
        {
            "foreground": "cashew",
            "background": "textured black surface"
        },
    ],
    "Level_2": [
        {
            "entity": ["cashew"],
            "number": ["1"],
            "location": ["center"],
            "entity_caption": ["A single cashew centered on a textured black surface"],
            "relation": "The cashew is placed centrally on a textured black background."
        },
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["light brown"],
            "texture": ["smooth"],
            "shape": ["kidney-shaped"]
        },
    ],
    "caption": "A single light brown cashew is centrally placed on a textured black background. The cashew has a smooth texture and a kidney shape."
    },
    {
    "Level_1": [
        {
            "foreground": "chewing gum",
            "background": "textured black surface"
        },
    ],
    "Level_2": [
        {
            "entity": ["chewing gum"],
            "number": ["1"],
            "location": ["center"],
            "entity_caption": ["A single piece of chewing gum"],
            "relation": "The chewing gum is centrally placed on a textured black background."
        },
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["white"],
            "texture": ["smooth"],
            "shape": ["rectangular"]
        },
    ],
    "caption": "A single piece of white chewing gum is centrally placed on a textured black background. The gum has a smooth texture and a rectangular shape."
    },
    {
    "Level_1": [
        {
            "foreground": "fryum",
            "background": "green textured surface"
        }
    ],
    "Level_2": [
        {
            "entity": ["fryum"],
            "number": ["1"],
            "location": ["center"],
            "entity_caption": ["A single fryum with a wheel-like structure"],
            "relation": "The fryum is located at the center of the image."
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["light orange"],
            "texture": ["smooth"],
            "shape": ["circular with radial spokes"]
        }
    ],
    "caption": "The image features a single fryum placed at the center of a green textured surface. The fryum is light orange in color, has a smooth texture, and is circular in shape with spokes resembling a wheel."
    },
    {
    "Level_1": [
        {
            "foreground": "macaroni",
            "background": "green"
        }
    ],
    "Level_2": [
        {
            "entity": ["macaroni", "macaroni", "macaroni", "macaroni"],
            "number": ["1", "1", "1", "1"],
            "location": ["top left", "top right", "bottom left", "bottom right"],
            "entity_caption": ["A piece of macaroni on the top left", "A piece of macaroni on the top right", "A piece of macaroni on the bottom left", "A piece of macaroni on the bottom right"],
            "relation": "Four macaroni pieces are arranged in a grid pattern, with two on the top row and two on the bottom row."
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None", "None"],
            "color": ["yellow", "yellow", "yellow", "yellow"],
            "texture": ["smooth", "smooth", "smooth", "smooth"],
            "shape": ["crescent", "crescent", "crescent", "crescent"]
        }
    ],
    "caption": "Four pieces of smooth, yellow crescent-shaped macaroni are neatly arranged against a textured green background, with two pieces positioned on the top and two on the bottom."
    },
    {
    "Level_1": [
        {
            "foreground": "macaroni",
            "background": "green textured"
        },
    ],
    "Level_2": [
        {
            "entity": ["macaroni", "macaroni", "macaroni", "macaroni"],
            "number": ["1", "1", "1", "1"],
            "location": ["top left", "top right", "bottom left", "bottom right"],
            "entity_caption": [
                "A single piece of macaroni on the top left",
                "A single piece of macaroni on the top right",
                "A single piece of macaroni on the bottom left",
                "A single piece of macaroni on the bottom right"
            ],
            "relation": "The four pieces of macaroni are arranged in a roughly square formation, with one piece in each quadrant."
        },
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None", "None"],
            "color": ["yellow", "yellow", "yellow", "yellow"],
            "texture": ["smooth", "smooth", "smooth", "smooth"],
            "shape": ["semi-circular", "semi-circular", "semi-circular", "semi-circular"]
        },
    ],
    "caption": "The image shows four pieces of yellow macaroni arranged on a green background. Each piece of macaroni is semi-circular in shape and has a smooth texture. They are positioned in a roughly square formation, with one piece in each quadrant: top-left, top-right, bottom-left, and bottom-right."
    },
    {
    "Level_1": [
        {
            "foreground": "printed circuit board",
            "background": "gray"
        }
    ],
    "Level_2": [
        {
            "entity": ["ultrasonic sensor", "pin header", "capacitor"],
            "number": ["2", "4", "1"],
            "location": ["left", "top", "center"],
            "entity_caption": [
                "two circular ultrasonic sensors positioned symmetrically",
                "one row of four pin headers at the top",
                "one cylindrical capacitor near the center",
            ],
            "relation": "The printed circuit board features two ultrasonic sensors on the left and right sides, four pin headers at the top, and a capacitor in the center."
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "vertical", "horizontal"],
            "color": ["silver", "silver", "silver"],
            "texture": ["smooth", "smooth", "smooth"],
            "shape": ["circular", "rectangular", "rectangular"]
        }
    ],
    "caption": "The image shows a printed circuit board (PCB) with a gray background. The PCB features two ultrasonic sensors located on the left and right sides, four vertical pins at the top center, and a single capacitor positioned at the center bottom. The ultrasonic sensors are silver in color, smooth in texture, and circular in shape. The pins are also silver, smooth, and rectangular. The capacitor is silver, smooth, and rectangular."
    },
    {
    "Level_1": [
        {
            "foreground": "printed circuit board",
            "background": "textured gray surface"
        }
    ],
    "Level_2": [
        {
            "entity": ["integrated circuit", "resistor", "capacitor", "pin header"],
            "number": ["3", "3", "2", "1"],
            "location": ["left", "center", "center", "top"],
            "entity_caption": [
                "Three black integrated circuits with multiple connecting pins",
                "Three resistors with color-coded bands",
                "Two capacitors of various sizes",
                "One pin header with multiple metal pins",
            ],
            "relation": "The printed circuit board has three integrated circuits located on the left, center, and right. There are three resistors distributed evenly across the board. Two capacitors are located near the center and right integrated circuits. A pin header is located at the top of the board."
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None", "vertical"],
            "color": ["black", "black", "black", "silver"],
            "texture": ["smooth", "smooth", "smooth", "smooth"],
            "shape": ["rectangular", "rectangular", "rectangular", "rectangular"]
        }
    ],
    "caption": "The image shows a printed circuit board (PCB) with a textured gray background. The PCB features three integrated circuits, one each on the left, center, and right. Three resistors are evenly distributed across the board, and two capacitors are located near the center and right integrated circuits. A pin header is positioned at the top of the board. The integrated circuits are black and rectangular, the resistors are blue and rectangular, the capacitors are black and rectangular, and the pin header is silver and rectangular. All components have a smooth texture."
    },
    {
    "Level_1": [
        {
            "foreground": "printed circuit board",
            "background": "textured green surface"
        }
    ],
    "Level_2": [
        {
            "entity": ["resistor", "capacitor", "LED", "pins", "potentiometer"],
            "number": ["4", "2", "2", "3", "1"],
            "location": ["center", "top left", "right", "left", "center"],
            "entity_caption": [
                "Four resistors located near the center of the board.",
                "Two capacitors located near the center of the board.",
                "Two LEDs, one transparent and one black, located at the top right and bottom right.",
                "Three metal pins located on the left side of the board.",
                "A blue potentiometer located at the center of the board.",
            ],
            "relation": "The printed circuit board has various components including resistors, capacitors, LEDs, a potentiometer, and pins. The resistors are located in the top-right, capacitors in the top left, LEDs in the right, the potentiometer in the center, and the pins on the left."
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None", "None", "None"],
            "color": ["black", "black", "transparent and black", "silver", "blue"],
            "texture": ["smooth", "smooth", "smooth", "smooth", "smooth"],
            "shape": ["cylindrical", "rectangular", "cylindrical", "cylindrical", "rectangular"]
        }
    ],
    "caption": "The image displays a printed circuit board (PCB) against a textured green surface. The PCB features several components: four black cylindrical resistors located at the top right, two black rectangular capacitors at the top left, two LEDs (one transparent and one black) on the right, three silver cylindrical pins on the left, and a blue rectangular potentiometer in the center. All components have a smooth texture."
    },
    {
    "Level_1": [
        {
            "foreground": "printed circuit board",
            "background": "textured black surface"
        }
    ],
    "Level_2": [
        {
            "entity": ["micro USB port", "resistor", "capacitor", "integrated circuit", "solder points"],
            "number": ["1", "2", "2", "1", "4"],
            "location": ["left", "top center", "center", "right center", "corners"],
            "entity_caption": [
                "A micro USB port is located on the left side of the board.",
                "Two resistors are positioned at the top center of the board.",
                "Two capacitors are situated in the center of the board.",
                "An integrated circuit is located at the right center of the board.",
                "Four solder points are located at the corners of the board."
            ],
            "relation": "The micro USB port is on the left side of the PCB. Two resistors are located at the top center. Two capacitors are positioned in the center. One integrated circuit is situated at the right center. Four soldering points are located at the corners."
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None", "None", "None"],
            "color": ["silver", "black", "yellow", "black", "silver"],
            "texture": ["smooth", "smooth", "smooth", "smooth", "smooth"],
            "shape": ["rectangular", "rectangular", "rectangular", "rectangular", "circular"]
        }
    ],
    "caption": "The image displays a printed circuit board (PCB) against a pure black background. The PCB features several components: a micro USB port located on the left, two resistors positioned at the top center, two capacitors in the center, an integrated circuit at the right center, and four solder points at the corners. The components exhibit various colors, including silver for the micro USB port and solder points, black for the resistors and integrated circuit, and yellow for the capacitors. All components have a smooth texture, with the micro USB port, the capacitors and integrated circuit being rectangular, and the solder points circular."
    },
    {
    "Level_1": [
        {
            "foreground": "pipe fryum",
            "background": "pure black"
        }
    ],
    "Level_2": [
        {
            "entity": ["pipe fryum"],
            "number": ["1"],
            "location": ["center"],
            "entity_caption": ["A single pipe fryum is positioned in the center of the image."],
            "relation": "The single pipe fryum is centrally located against a pure black background."
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["light beige"],
            "texture": ["rough"],
            "shape": ["cylindrical"]
        }
    ],
    "caption": "The image features a single pipe fryum positioned centrally against a pure black background. The fryum is light beige in color, has a rough texture, and is cylindrical in shape."
    }
]

#这里面放所有类别的细粒度描述，做一个list来映射对应的类别和索引
fine_grained_normal_prompts_v3 = [
    {
    "Level_1": [
        {
            "foreground": "bottle",
            "background": "pure white"
        }
    ],
    "Level_2": [
        {
            "entity": ["bottle"],
            "number": ["1"],
            "location": ["center"],
            "relation": "The bottle is centrally located in the image."
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["black"],
            "texture": ["smooth"],
            "shape": ["circular"],
            "entity_caption": ["A single bottle with black color, circular shape and smooth texture, is positioned at the center of the image, viewed from the top."],
        }
    ],
    "caption": "The image shows a single black circular bottle positioned centrally against a pure white background. The bottle has a smooth texture and is viewed from the top, highlighting its circular opening."
    },
    {
    "Level_1": [
        {
            "foreground": "cable",
            "background": "gray textured surface"
        }
    ],
    "Level_2": [
        {
            "entity": ["yellow wire", "blue wire", "brown wire"],
            "number": ["1", "1", "1"],
            "location": ["top right", "bottom left", "bottom right"],
            "relation": "The three wires are bundled together within a circular cable sheath, with the yellow wire positioned at the top right, the blue wire at the bottom left, and the brown wire at the bottom right."
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None"],
            "color": ["yellow", "blue", "brown"],
            "texture": ["smooth", "smooth", "smooth"],
            "shape": ["cylindrical", "cylindrical", "cylindrical"],
            "entity_caption": [
                "A yellow wire with copper strands at the top right. It has a smooth texture and a cylindrical shape.",
                "A blue wire with copper strands at the bottom left. It has a smooth texture and a cylindrical shape.",
                "A brown wire with copper strands at the bottom right. It has a smooth texture and a cylindrical shape."
            ]
        }
    ],
    "caption": "The image shows a close-up view of a cable with three distinct wires inside a circular sheath. The wires are colored yellow, blue, and brown, and are positioned at the top right, bottom left, and bottom right respectively. Each wire has a smooth texture and a cylindrical shape, and the cable is set against a gray textured surface."
    },
    {
    "Level_1": [
        {
            "foreground": "capsule",
            "background": "white"
        }
    ],
    "Level_2": [
        {
            "entity": ["capsule"],
            "number": ["1"],
            "location": ["center"],
            "relation": "The capsule is centrally placed against a pure white background."
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["black", "orange"],
            "texture": ["smooth"],
            "shape": ["cylindrical"],
            "entity_caption": ["The capsule has a smooth texture with a cylindrical shape. It is colored black on one half and orange on the other half. The black half has the text 'actavis' printed on it, and the orange half has the number '500' printed on it."]
        }
    ],
    "caption": "The image features a single capsule placed horizontally in the center against a pure white background. The capsule is cylindrical in shape with a smooth texture. It has two distinct colors: the left half is black with the text 'actavis' printed on it, and the right half is orange with the number '500' printed on it."
    },
    {
    "Level_1": [
        {
            "foreground": "carpet",
            "background": "none"
        },
    ],
    "Level_2": [
        {
            "entity": ["woven fibers"],
            "number": ["multiple"],
            "location": ["throughout"],
            "relation": "The woven fibers are uniformly distributed throughout the image, creating a consistent texture."
        },
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["gray"],
            "texture": ["rough"],
            "shape": ["rectangular"],
            "entity_caption": ["The woven fibers are gray in color, have a rough texture and a rectangular shape."]
        },
    ],
    "caption": "This image showcases a close-up view of a carpet with interlaced woven fibers. The fibers are predominantly gray, with hints of black and white, creating a textured appearance. The shape of the visible carpet area is rectangular, and the intricate weaving pattern is consistent throughout the image, indicating a uniform manufacturing process."
    },
    {
    "Level_1": [
        {
            "foreground": "grid",
            "background": "gray"
        }
    ],
    "Level_2": [
        {
            "entity": ["diamond-shaped grid pattern"],
            "number": ["multiple"],
            "location": ["center"],
            "relation": "The grid is centrally located and spans the entire image."
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["silver"],
            "texture": ["smooth"],
            "shape": ["diamond-shaped"],
            "entity_caption": ["The grid pattern is silver in color, has a smooth texture, and consists of diamond-shaped pattern."]
        }
    ],
    "caption": "The image features a centrally located silver grid with a diamond shape pattern against a gray background. The grid spans the entire image and has a smooth texture."
    },
    {
    "Level_1": [
        {
            "foreground": "hazelnut",
            "background": "pure black"
        },
    ],
    "Level_2": [
        {
            "entity": ["hazelnut"],
            "number": ["1"],
            "location": ["center"],
            "relation": "The hazelnut is centrally located against a pure black background."
        },
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["brown"],
            "texture": ["smooth"],
            "shape": ["spherical"],
            "entity_caption": ["The hazelnut is brown in color with a smooth texture. It has an spherical shape."]
        },
    ],
    "caption": "A single brown hazelnut with a smooth texture and a spherical shape is centered against a pure black background."
    },
    {
    "Level_1": [
        {
            "foreground": "leather",
            "background": "none"
        },
    ],
    "Level_2": [
        {
            "entity": ["leather texture"],
            "number": ["1"],
            "location": ["center"],
            "relation": "The leather texture occupies the entire image, centered within the frame."
        },
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["brown"],
            "texture": ["rough"],
            "shape": ["irregular"],
            "entity_caption": ["The leather has a rough texture with an irregular pattern and is brown in color."]
        },
    ],
    "caption": "The image showcases a piece of brown leather with a rough, irregular texture. The leather occupies the entire image, centered within the frame."
    },
    {
    "Level_1": [
        {
            "foreground": "metal nut",
            "background": "pure black"
        },
    ],
    "Level_2": [
        {
            "entity": ["metal nut"],
            "number": ["1"],
            "location": ["center"],
            "relation": "The metal nut is positioned centrally against a pure black background."
        },
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["metallic silver"],
            "texture": ["rough"],
            "shape": ["circular shape with four distinct protruding edges"],
            "entity_caption": ["The metal nut is metallic silver in color, with a rough texture. It has a circular shape with four distinct protruding edges."]
        },
    ],
    "caption": "A single metallic silver metal nut with a rough surface is centered against a pure black background. The metal nut has a circular shape with four distinct protruding edges."
    },
    {
    "Level_1": [
        {
            "foreground": "pill",
            "background": "pure black"
        },
    ],
    "Level_2": [
        {
            "entity": ["pill"],
            "number": ["1"],
            "location": ["center"],
            "relation": "The pill is centrally located against a pure black background."
        },
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["white with red specks"],
            "texture": ["smooth"],
            "shape": ["oval"],
            "entity_caption": ["The pill is oval-shaped, white with red specks, and has a smooth texture. It has the letters 'FF' engraved on its surface."]
        },
    ],
    "caption": "A single oval-shaped pill with a smooth texture and white color, speckled with red spots, prominently embossed with the letters 'FF' in the center, set against a pure black background."
    },
    {
    "Level_1": [
        {
            "foreground": "screw",
            "background": "light grey"
        }
    ],
    "Level_2": [
        {
            "entity": ["screw"],
            "number": ["1"],
            "location": ["center"],
            "relation": "The screw is positioned at the center of the image."
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["metallic grey"],
            "texture": ["smooth and threaded"],
            "shape": ["cylindrical with a conical head"],
            "entity_caption": ["The screw is metallic grey in color, with a smooth and threaded texture. It's shape is cylindrical with a conical head."]
        }
    ],
    "caption": "A single metallic gray screw is centered against a light gray background. The screw has a smooth cylindrical body with a threaded section, a pointed tip, and a flat head."
    },
    {
    "Level_1": [
        {
            "foreground": "tile",
            "background": "None"
        }
    ],
    "Level_2": [
        {
            "entity": ["speckles"],
            "number": ["multiple"],
            "location": ["throughout"],
            "relation": "The speckles are evenly distributed across the entire surface of the tile."
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["grey"],
            "texture": ["granular"],
            "shape": ["irregular"],
            "entity_caption": ["The speckles are scattered across the tile, with grey color, granular texture and irregular shape."],
        }
    ],
    "caption": "The image displays a close-up view of a tile with a granular texture, featuring a multitude of irregularly shaped grey, black, and white speckles that are evenly distributed throughout the surface, creating a consistent pattern."
    },
    {
    "Level_1": [
        {
            "foreground": "toothbrush",
            "background": "pure black"
        },
    ],
    "Level_2": [
        {
            "entity": ["bristle clusters", "toothbrush handle"],
            "number": ["multiple", "1"],
            "location": ["center", "bottom"],
            "relation": "The bristle clusters are mounted on the head of the toothbrush handle."
        },
    ],
    "Level_3": [
        {
            "direction": ["upward", "None"],
            "color": ["blue and white", "white"],
            "texture": ["bristled", "smooth"],
            "shape": ["rounded", "elongated"],
            "entity_caption": ["Multiple bristle clusters have blue and white color, bristled texture and rounded shape.", "The toothbrush handle is white in color, smooth in texture, and elongated in shape."]
        },
    ],
    "caption": "A close-up image of a toothbrush with a white handle. The head of the toothbrush features many clusters of bristles, with a mix of blue and white colors. The bristles are arranged in a pattern and are oriented upward, indicating the brushing surface. The handle appears smooth and elongated, contrasting with the textured bristles. The entire toothbrush is set against a pure black background, highlighting its details."
    },
    {
    "Level_1": [
        {
            "foreground": "transistor",
            "background": "brown circuit board with circular holes"
        }
    ],
    "Level_2": [
        {
            "entity": ["transistor body", "transistor legs", "circuit board", "holes"],
            "number": ["1", "3", "1", "multiple"],
            "location": ["center", "bottom", "entire image", "evenly distributed"],
            "relation": "The transistor is mounted on the circuit board, with its legs inserted through the holes."
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "downward", "None", "None"],
            "color": ["black", "metallic silver", "brown", "dark brown"],
            "texture": ["smooth", "metallic", "smooth", "smooth"],
            "shape": ["rectangular", "straight", "rectangular with multiple holes", "circular"],
            "entity_caption": [
                "A black rectangular transistor body with smooth texture and rectangular shape", 
                "Three metallic silver transistor legs with straight shape and metallic texture", 
                "A brown circuit board with a smooth texture and rectangular with multiple holes.", 
                "Multiple dark brown circular holes on the circuit board, with smooth texture."]
        }
    ],
    "caption": "A black, smooth-textured transistor with three metallic legs is centrally mounted on a brown circuit board featuring multiple evenly distributed dark brown circular holes. The legs of the transistor are inserted downward through the holes of the circuit board."
    },
    {
    "Level_1": [
        {
            "foreground": "wood",
            "background": "none"
        }
    ],
    "Level_2": [
        {
            "entity": ["wood grain pattern"],
            "number": ["1"],
            "location": ["throughout"],
            "relation": "The wood grain pattern is consistent and covers the entire image."
        }
    ],
    "Level_3": [
        {
            "direction": ["vertical"],
            "color": ["various shades of brown"],
            "texture": ["smooth"],
            "shape": ["flat"],
            "entity_caption": ["A wood grain pattern with various shades of brown colors, smooth texture, and flat shape."],
        }
    ],
    "caption": "The image displays a vertical wood grain pattern with various shades of brown colors, indicating a smooth texture and elongated shapes throughout the surface."
    },
    {
    "Level_1": [
        {
            "foreground": "zipper",
            "background": "textured fabric"
        }
    ],
    "Level_2": [
        {
            "entity": ["zipper teeth", "zipper tapes"],
            "number": ["multiple", "2"],
            "location": ["center", "both sides"],
            "relation": "The zipper teeth are aligned in the center, flanked by the zipper tapes on both sides."
        }
    ],
    "Level_3": [
        {
            "direction": ["vertical", "vertical"],
            "color": ["black", "black"],
            "texture": ["smooth", "rough"],
            "shape": ["interlock", "flat"],
            "entity_caption": ["The metallic black zipper teeth are interlocked in the center with vertical direction and smooth texture", "The fabric black zipper tapes are running parallel on both sides of the zipper teeth, and the zipper tapes have a rough texture and flat shape."],
        }
    ],
    "caption": "A close-up view of a zipper with multiple dark gray interlocking teeth aligned vertically in the center, flanked by two flat black zipper tapes with a textured surface on both sides."
    },
    {
    "Level_1": [
        {
            "foreground": "candles",
            "background": "black"
        }
    ],
    "Level_2": [
        {
            "entity": ["candle", "candle", "candle", "candle"],
            "number": ["1", "1", "1", "1"],
            "location": ["top left", "top right", "bottom left", "bottom right"],
            "relation": "The candles are arranged in a 2x2 grid pattern."
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None", "None"],
            "color": ["white", "white", "white", "white"],
            "texture": ["smooth", "smooth", "smooth", "smooth"],
            "shape": ["circular", "circular", "circular", "circular"],
            "entity_caption": [
                "A unlit candle with a wick visible on the top left, the candle has white color, smooth texture, and circular shape.", 
                "A unlit candle with a wick visible on the top right, the candle has white color, smooth texture, and circular shape.", 
                "A unlit candle with a wick visible on the bottom left, the candle has white color, smooth texture, and circular shape.", 
                "A unlit candle with a wick visible on the bottom right, the candle has white color, smooth texture, and circular shape."
            ],
        }
    ],
    "caption": "The image displays four white, smooth, circular candles arranged in a 2x2 grid pattern against a black background. Each candle is positioned in one of the four quadrants: top-left, top-right, bottom-left, and bottom-right."
    },
    {
    "Level_1": [
        {
            "foreground": "capsules",
            "background": "gray textured surface"
        }
    ],
    "Level_2": [
        {
            "entity": ["capsule"],
            "number": ["multiple"],
            "location": ["scattered"],
            "relation": "The capsules are scattered randomly across the gray textured surface."
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["green"],
            "texture": ["smooth"],
            "shape": ["oval"],
            "entity_caption": ["Multiple green translucent capsules with smooth texture and oval shape."],
        }
    ],
    "caption": "The image displays multiple green capsules scattered randomly on a gray textured surface. Each capsule is smooth and oval-shaped."
    },
    {
    "Level_1": [
        {
            "foreground": "cashew",
            "background": "textured black surface"
        },
    ],
    "Level_2": [
        {
            "entity": ["cashew"],
            "number": ["1"],
            "location": ["center"],
            "relation": "The cashew is placed centrally on a textured black background."
        },
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["light brown"],
            "texture": ["smooth"],
            "shape": ["kidney-shaped"],
            "entity_caption": ["A cashew at the center of the textured black surface background and has a light brown color, smooth texture, and kidney-shaped."],
        },
    ],
    "caption": "A single light brown cashew is centrally placed on a textured black background. The cashew has a smooth texture and kidney-shaped."
    },
    {
    "Level_1": [
        {
            "foreground": "chewing gum",
            "background": "textured black surface"
        },
    ],
    "Level_2": [
        {
            "entity": ["chewing gum"],
            "number": ["1"],
            "location": ["center"],
            "relation": "The chewing gum is centrally placed on a textured black background."
        },
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["white"],
            "texture": ["smooth"],
            "shape": ["rectangular"],
            "entity_caption": ["A single piece of smooth, white chewing gum in a rectangular shape."]
        },
    ],
    "caption": "A single piece of white chewing gum is centrally placed on a textured black background. The gum has a smooth texture and a rectangular shape."
    },
    {
    "Level_1": [
        {
            "foreground": "fryum",
            "background": "green textured surface"
        }
    ],
    "Level_2": [
        {
            "entity": ["fryum"],
            "number": ["1"],
            "location": ["center"],
            "relation": "The fryum is located at the center of the image."
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["light orange"],
            "texture": ["smooth"],
            "shape": ["circular with radial spokes"],
            "entity_caption": ["A light orange fryum have a circular with radial spokes shape, presenting a smooth texture."]
        }
    ],
    "caption": "The image features a single fryum placed at the center of a green textured surface. The fryum is light orange in color, has a smooth texture, and is circular in shape with spokes resembling a wheel."
    },
    {
    "Level_1": [
        {
            "foreground": "macaroni",
            "background": "green"
        }
    ],
    "Level_2": [
        {
            "entity": ["macaroni", "macaroni", "macaroni", "macaroni"],
            "number": ["1", "1", "1", "1"],
            "location": ["top left", "top right", "bottom left", "bottom right"],
            "relation": "Four macaroni pieces are arranged in a grid pattern, with two on the top row and two on the bottom row."
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None", "None"],
            "color": ["yellow", "yellow", "yellow", "yellow"],
            "texture": ["smooth", "smooth", "smooth", "smooth"],
            "shape": ["crescent", "crescent", "crescent", "crescent"],
            "entity_caption": [
                "A piece of yellow macaroni on the top left with crescent shape and smooth texture.", 
                "A piece of yellow macaroni on the top right with crescent shape and smooth texture.", 
                "A piece of yellow macaroni on the bottom left with crescent shape and smooth texture.", 
                "A piece of yellow macaroni on the bottom right with crescent shape and smooth texture."
            ],
        }
    ],
    "caption": "Four pieces of smooth, yellow crescent-shaped macaroni are neatly arranged against a textured green background, with two pieces positioned on the top and two on the bottom."
    },
    {
    "Level_1": [
        {
            "foreground": "macaroni",
            "background": "green textured"
        },
    ],
    "Level_2": [
        {
            "entity": ["macaroni", "macaroni", "macaroni", "macaroni"],
            "number": ["1", "1", "1", "1"],
            "location": ["top left", "top right", "bottom left", "bottom right"],
            "relation": "The four pieces of macaroni are arranged in a roughly square formation, with one piece in each quadrant."
        },
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None", "None"],
            "color": ["yellow", "yellow", "yellow", "yellow"],
            "texture": ["smooth", "smooth", "smooth", "smooth"],
            "shape": ["semi-circular", "semi-circular", "semi-circular", "semi-circular"],
            "entity_caption": [
                "A single yellow piece of macaroni on the top left with a semi-circular shape and smooth texture.",
                "A single yellow piece of macaroni on the top right with a semi-circular shape and smooth texture.",
                "A single yellow piece of macaroni on the bottom left with a semi-circular shape and smooth texture.",
                "A single yellow piece of macaroni on the bottom right with a semi-circular shape and smooth texture."
            ]
        },
    ],
    "caption": "The image shows four pieces of yellow macaroni arranged on a green textured background. Each piece of macaroni is semi-circular in shape and has a smooth texture. They are positioned in a roughly square formation, with one piece in each quadrant: top-left, top-right, bottom-left, and bottom-right."
    },
    {
    "Level_1": [
        {
            "foreground": "printed circuit board",
            "background": "gray"
        }
    ],
    "Level_2": [
        {
            "entity": ["ultrasonic sensor", "pin header", "capacitor"],
            "number": ["2", "4", "1"],
            "location": ["left", "top", "center"],
            "relation": "The printed circuit board features two ultrasonic sensors on the left and right sides, four pin headers at the top, and a capacitor in the center."
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "vertical", "horizontal"],
            "color": ["silver", "silver", "silver"],
            "texture": ["smooth", "smooth", "smooth"],
            "shape": ["circular", "rectangular", "rectangular"],
            "entity_caption": [
                "two circular silver ultrasonic sensors positioned symmetrically on the left and right sides, with a smooth texture and circular shape.",
                "one row of four silver pin headers at the top of the board, with a smooth texture and rectangular shape.",
                "one rectangular silver capacitor near the center of the board, with a smooth texture and rectangular shape.",
            ],
        }
    ],
    "caption": "The image shows a printed circuit board (PCB) with a gray background. The PCB features two ultrasonic sensors located on the left and right sides, four vertical pins at the top center, and a single capacitor positioned at the center bottom. The ultrasonic sensors are silver in color, smooth in texture, and circular in shape. The pins are also silver, smooth, and rectangular. The capacitor is silver, smooth, and rectangular."
    },
    {
    "Level_1": [
        {
            "foreground": "printed circuit board",
            "background": "textured gray surface"
        }
    ],
    "Level_2": [
        {
            "entity": ["integrated circuit", "resistor", "capacitor", "pin header"],
            "number": ["3", "3", "2", "1"],
            "location": ["left", "center", "center", "top"],
            "relation": "The printed circuit board has three integrated circuits located on the left, center, and right. There are three resistors distributed evenly across the board. Two capacitors are located near the center and right integrated circuits. A pin header is located at the top of the board."
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None", "vertical"],
            "color": ["black", "black", "black", "silver"],
            "texture": ["smooth", "smooth", "smooth", "smooth"],
            "shape": ["rectangular", "rectangular", "rectangular", "rectangular"],
            "entity_caption": [
                "Three black rectangular integrated circuits with multiple connecting pins, the integrated circuits have a smooth texture.",
                "Three black resistors with color-coded bands, the resistors have a smooth texture and rectangular shape.",
                "Two blcak capacitors with a smooth texture and rectangular shape.",
                "One silver pin header with multiple metal pins, the pin header has a smooth texture and rectangular shape.",
            ],
        }
    ],
    "caption": "The image shows a printed circuit board (PCB) with a textured gray background. The PCB features three integrated circuits, one each on the left, center, and right. Three resistors are evenly distributed across the board, and two capacitors are located near the center and right integrated circuits. A pin header is positioned at the top of the board. The integrated circuits are black and rectangular, the resistors are blue and rectangular, the capacitors are black and rectangular, and the pin header is silver and rectangular. All components have a smooth texture."
    },
    {
    "Level_1": [
        {
            "foreground": "printed circuit board",
            "background": "textured green surface"
        }
    ],
    "Level_2": [
        {
            "entity": ["resistor", "capacitor", "LED", "pins", "potentiometer"],
            "number": ["4", "2", "2", "3", "1"],
            "location": ["center", "top left", "right", "left", "center"],
            "relation": "The printed circuit board has various components including resistors, capacitors, LEDs, a potentiometer, and pins. The resistors are located in the top-right, capacitors in the top left, LEDs in the right, the potentiometer in the center, and the pins on the left."
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None", "None", "None"],
            "color": ["black", "black", "transparent and black", "silver", "blue"],
            "texture": ["smooth", "smooth", "smooth", "smooth", "smooth"],
            "shape": ["cylindrical", "rectangular", "cylindrical", "cylindrical", "rectangular"],
            "entity_caption": [
                "Four black resistors located near the center of the board, each resistor has a smooth texture and cylindrical shape.",
                "Two capacitors located near the center of the board, each capacitor has a smooth texture and rectangular shape.",
                "Two LEDs, one transparent and one black, located at the top right and bottom right. Both LEDs have a smooth texture and cylindrical shape.",
                "Three silver metal pins located on the left side of the board. Both pins have a smooth texture and cylindrical shape.",
                "A blue potentiometer located at the center of the board with smooth texture and rectangular shape.",
            ],
        }
    ],
    "caption": "The image displays a printed circuit board (PCB) against a textured green surface. The PCB features several components: four black cylindrical resistors located at the top right, two black rectangular capacitors at the top left, two LEDs (one transparent and one black) on the right, three silver cylindrical pins on the left, and a blue rectangular potentiometer in the center. All components have a smooth texture."
    },
    {
    "Level_1": [
        {
            "foreground": "printed circuit board",
            "background": "textured black surface"
        }
    ],
    "Level_2": [
        {
            "entity": ["micro USB port", "resistor", "capacitor", "integrated circuit", "solder points"],
            "number": ["1", "2", "2", "1", "4"],
            "location": ["left", "top center", "center", "right center", "corners"],
            "relation": "The micro USB port is on the left side of the PCB. Two resistors are located at the top center. Two capacitors are positioned in the center. One integrated circuit is situated at the right center. Four soldering points are located at the corners."
        }
    ],
    "Level_3": [
        {
            "direction": ["None", "None", "None", "None", "None"],
            "color": ["silver", "black", "yellow", "black", "silver"],
            "texture": ["smooth", "smooth", "smooth", "smooth", "smooth"],
            "shape": ["rectangular", "rectangular", "rectangular", "rectangular", "circular"],
            "entity_caption": [
                "A silver micro USB port is located on the left side of the board, the port has a smooth texture and rectangular shape.",
                "Two black resistors are positioned at the top center of the board, both resistors have a smooth texture and rectangular shape.",
                "Two yellow capacitors are situated in the center of the board, both capacitors have a smooth texture and rectangular shape.",
                "A black integrated circuit is located at the right center of the board, the circuit has a smooth texture and rectangular shape.",
                "Four silver solder points are located at the corners of the board, all solder points have a smooth texture and circular shape.",
            ],
        }
    ],
    "caption": "The image displays a printed circuit board (PCB) against a pure black background. The PCB features several components: a micro USB port located on the left, two resistors positioned at the top center, two capacitors in the center, an integrated circuit at the right center, and four solder points at the corners. The components exhibit various colors, including silver for the micro USB port and solder points, black for the resistors and integrated circuit, and yellow for the capacitors. All components have a smooth texture, with the micro USB port, the capacitors and integrated circuit being rectangular, and the solder points circular."
    },
    {
    "Level_1": [
        {
            "foreground": "pipe fryum",
            "background": "pure black"
        }
    ],
    "Level_2": [
        {
            "entity": ["pipe fryum"],
            "number": ["1"],
            "location": ["center"],
            "relation": "The single pipe fryum is centrally located against a pure black background."
        }
    ],
    "Level_3": [
        {
            "direction": ["None"],
            "color": ["light beige"],
            "texture": ["rough"],
            "shape": ["cylindrical"],
            "entity_caption": ["A light beige pipe fryum is positioned in the center of the image, the fryum has a rough texture and cylindrical shape."]
        }
    ],
    "caption": "The image features a single pipe fryum positioned centrally against a pure black background. The fryum is light beige in color, has a rough texture, and is cylindrical in shape."
    }
]






#用来映射类别和对应的细粒度描述
total_classes2id = {
    'bottle': 0,
    'cable': 1,
    'capsule': 2,
    'carpet': 3,
    'grid': 4,
    'hazelnut': 5,
    'leather': 6,
    'metal_nut': 7,
    'pill': 8,
    'screw': 9,
    'tile': 10,
    'toothbrush': 11,
    'transistor': 12,
    'wood': 13,
    'zipper': 14,
    ###下面是VisA：
    'candle': 15,
    'capsules': 16,
    'cashew': 17,
    'chewinggum': 18,
    'fryum': 19,
    'macaroni1': 20, #两种macaroni不能用同一个id，因为存在很多不同的描述
    'macaroni2': 21,
    'pcb1': 22,
    'pcb2': 23,
    'pcb3': 24,
    'pcb4': 25,
    'pipe_fryum':26
}

#这些是Level_3出现的所有Color, Texture, Shape的list，主要用来做handle abnormal prompts(具体采样方法可以再研究研究，现阶段先用随机采样的方式吧~)
fine_grained_color_list = ['black', 'blue and white', 'brown', 'gray', 'green', 'grey', 'light beige', 'light brown', 'light orange', 'metallic grey', 'metallic silver', 'silver', 'various shades of brown', 'white', 'white with red specks', 'yellow']

fine_grained_texture_list = ['bristled', 'granular', 'rough', 'smooth', 'smooth and threaded', 'textured', 'fuzzy', 'crinkled', 'knitted', 'woven']

fine_grained_shape_list = ['circular', 'circular shape with four distinct protruding edges', 'circular with radial spokes', 'crescent', 'cylindrical', 'cylindrical with a conical head', 'diamond-shaped', 'flat', 'interlock', 'irregular', 'kidney-shaped', 'oval', 'rectangular', 'rounded', 'semi-circular', 'spherical']

fine_grained_entity_list = ['LED', 'blue wire', 'bottle', 'bristle clusters', 'brown wire', 'candle', 'capacitor', 'capsule', 'cashew', 'chewing gum', 'circuit board', 'diamond-shaped grid pattern', 'fryum', 'hazelnut', 'holes', 'integrated circuit', 'leather texture', 'macaroni', 'metal nut', 'micro USB port', 'pill', 'pin header', 'pins', 'pipe fryum', 'potentiometer', 'resistor', 'screw', 'solder points', 'speckles', 'toothbrush handle', 'transistor body', 'transistor legs', 'ultrasonic sensor', 'wood grain pattern', 'woven fibers', 'yellow wire', 'zipper tapes', 'zipper teeth']

fine_grained_location_list = ['both sides', 'bottom', 'bottom left', 'bottom right', 'center', 'corners', 'entire image', 'evenly distributed', 'left', 'right', 'right center', 'scattered', 'throughout', 'top', 'top center', 'top left', 'top right']

fine_grained_number_list = ['1', '2', '3', '4', 'multiple']

if __name__ == '__main__':
    #将fine_grained_normal_prompts_v2中的Level_3里color, texture, shape中出现过的词提取出来，放入一个不重复的set中，并转为list后按字母序升序打印输出
    all_words_color = set()
    all_words_texture = set()
    all_words_shape = set()
    all_words_entity = set()
    all_words_location = set()
    all_words_number = set()
    
    for i in fine_grained_normal_prompts_v3:
        for j in i['Level_3']:
            all_words_color.add(j['color'][0])
            all_words_texture.add(j['texture'][0])
            all_words_shape.add(j['shape'][0])
        for j in i['Level_2']:
            for k in range(len(j['entity'])):
                all_words_entity.add(j['entity'][k])
            # for k in len()
                all_words_location.add(j['location'][k])
                all_words_number.add(j['number'][k])
    
    all_words_color = list(all_words_color)
    all_words_texture = list(all_words_texture)
    all_words_shape = list(all_words_shape)
    all_words_entity = list(all_words_entity)
    all_words_location = list(all_words_location)
    all_words_number = list(all_words_number)
    
    all_words_color.sort()
    all_words_texture.sort()
    all_words_shape.sort()
    all_words_entity.sort()
    all_words_location.sort()
    all_words_number.sort()
    
    print("Color List:", all_words_color)
    print("Texture List:", all_words_texture)
    print("Shape List:", all_words_shape)
    print("Entity List:", all_words_entity)
    print("Location List:", all_words_location)
    print("Number List:", all_words_number)