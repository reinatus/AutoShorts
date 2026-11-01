extends Node2D

const W := 1080.0
const H := 1920.0
const SCENE_SECONDS := 5.0
const DURATION := 40.0
const FPS := 30
const CAPTIONS := [
	["EN ESTE LUGAR DEL ÁRTICO,", "MORIR ES CASI IMPOSIBLE"],
	["LONGYEARBYEN ESTÁ ENTRE", "MONTAÑAS Y UN FIORDO"],
	["EL SUELO PERMANECE", "CONGELADO TODO EL AÑO"],
	["SU CEMENTERIO DEJÓ DE", "ACEPTAR ENTIERROS"],
	["NO ES UNA LEY:", "EL PROBLEMA ES EL HIELO"],
	["LOS ENFERMOS GRAVES", "SON TRASLADADOS A NORUEGA"],
	["EL MITO DICE: AQUÍ ESTÁ", "PROHIBIDO MORIR"],
	["LA REALIDAD ES MÁS EXTRAÑA", "QUE EL PROPIO MITO"],
]

var elapsed := 0.0
var audio_phase := 0.0
var audio_playback: AudioStreamGeneratorPlayback
var font: Font

func _ready() -> void:
	font = ThemeDB.fallback_font
	var generator := AudioStreamGenerator.new()
	generator.mix_rate = 44100.0
	generator.buffer_length = 0.5
	var player := AudioStreamPlayer.new()
	player.stream = generator
	add_child(player)
	player.play()
	audio_playback = player.get_stream_playback()

func _process(delta: float) -> void:
	# `--quit-after` defines the exact frame count; this clock follows frames actually drawn.
	elapsed = float(Engine.get_frames_drawn()) / float(FPS)
	_fill_audio()
	queue_redraw()

func _fill_audio() -> void:
	if audio_playback == null:
		return
	var available := audio_playback.get_frames_available()
	for i in available:
		var beat: float = 0.45 + 0.55 * maxf(0.0, sin(elapsed * TAU * 0.5))
		var sample: float = (sin(audio_phase) * 0.018 + sin(audio_phase * 0.5) * 0.009) * beat
		audio_playback.push_frame(Vector2(sample, sample))
		audio_phase = fmod(audio_phase + TAU * 110.0 / 44100.0, TAU)

func _draw() -> void:
	var scene := mini(7, int(elapsed / SCENE_SECONDS))
	var t := fmod(elapsed, SCENE_SECONDS) / SCENE_SECONDS
	_draw_background(scene, t)
	# Every shot changes geometry over time: this is rendered animation, not a zoomed still.
	match scene:
		0: _draw_hook(t)
		1: _draw_town(t)
		2: _draw_permafrost(t)
		3: _draw_cemetery(t)
		4: _draw_ice_problem(t)
		5: _draw_transfer(t)
		6: _draw_myth(t)
		7: _draw_finale(t)
	_draw_caption(scene, t)
	_draw_progress()
	var fade: float = maxf(1.0 - _smooth(0.0, 0.08, t), _smooth(0.90, 1.0, t))
	if fade > 0.0:
		draw_rect(Rect2(0, 0, W, H), Color(0.015, 0.025, 0.07, fade))

func _draw_background(scene: int, t: float) -> void:
	var palettes := [
		[Color("07142f"), Color("164b72")], [Color("071932"), Color("17617c")],
		[Color("07162a"), Color("24758a")], [Color("08162c"), Color("3b6682")],
		[Color("0a1730"), Color("17445e")], [Color("071b35"), Color("2a6e8a")],
		[Color("100f31"), Color("49336c")], [Color("030b20"), Color("155571")],
	]
	var colors = palettes[scene]
	for i in 24:
		var y := H * float(i) / 24.0
		var c: Color = colors[0].lerp(colors[1], float(i) / 23.0)
		draw_rect(Rect2(0, y, W, H / 24.0 + 2), c)
	for i in 70:
		var x := fmod(float(i * 197 + scene * 71) + elapsed * (18.0 + i % 7), W)
		var y := fmod(float(i * 83 + scene * 113) + elapsed * (30.0 + i % 5), H)
		draw_circle(Vector2(x, y), 2.0 + i % 4, Color(0.85, 0.96, 1.0, 0.35))

func _draw_hook(t: float) -> void:
	var pulse := 1.0 + 0.08 * sin(t * TAU * 3.0)
	var center := Vector2(W / 2, 820)
	draw_circle(center, 245 * pulse, Color("2cb5c9"))
	draw_circle(center, 205 * pulse, Color("071a38"))
	for i in 16:
		var a := t * TAU + float(i) * TAU / 16.0
		var p := center + Vector2(cos(a), sin(a)) * 330.0
		draw_circle(p, 10 + i % 3 * 5, Color("d8fbff"))
	var pin := center + Vector2(sin(t * TAU) * 85, -35 + cos(t * TAU * 2) * 30)
	draw_circle(pin, 54, Color("ff5d73"))
	draw_colored_polygon(PackedVector2Array([pin + Vector2(-38, 20), pin + Vector2(38, 20), pin + Vector2(0, 130)]), Color("ff5d73"))
	draw_circle(pin, 18, Color("fff2cf"))

func _mountain(points: PackedVector2Array, color: Color) -> void:
	draw_colored_polygon(points, color)

func _draw_town(t: float) -> void:
	var drift := sin(t * TAU) * 45.0
	_mountain(PackedVector2Array([Vector2(-80 + drift, 1160), Vector2(230 + drift, 440), Vector2(560 + drift, 1160)]), Color("1b4a68"))
	_mountain(PackedVector2Array([Vector2(380 + drift, 1160), Vector2(790 + drift, 360), Vector2(1210 + drift, 1160)]), Color("245c76"))
	for i in 9:
		var x := 70.0 + i * 115.0 - t * 35.0
		var h := 170.0 + (i % 3) * 65.0
		draw_rect(Rect2(x, 1180 - h, 92, h), Color("102238"))
		draw_colored_polygon(PackedVector2Array([Vector2(x - 12, 1180 - h), Vector2(x + 46, 1120 - h), Vector2(x + 104, 1180 - h)]), Color("d4594d"))
		for wy in 2:
			for wx in 2:
				draw_rect(Rect2(x + 17 + wx * 40, 1205 - h + wy * 58, 20, 28), Color("ffd772", 0.5 + 0.5 * sin(t * TAU * 2 + i)))
	_draw_aurora(t, 280)

func _draw_aurora(t: float, base_y: float) -> void:
	for band in 5:
		var pts := PackedVector2Array()
		for i in 28:
			var x := float(i) * W / 27.0
			var y := base_y + band * 34.0 + sin(i * 0.45 + t * TAU * (0.5 + band * 0.08)) * (55 + band * 7)
			pts.append(Vector2(x, y))
		draw_polyline(pts, Color(0.25, 1.0, 0.68, 0.24), 22.0 - band * 3.0, true)

func _draw_permafrost(t: float) -> void:
	draw_rect(Rect2(0, 1000, W, 920), Color("123b53"))
	for layer in 6:
		draw_rect(Rect2(0, 1050 + layer * 140, W, 90), Color("1d6572").darkened(layer * 0.055))
	var drill_x := 260.0 + t * 540.0
	draw_rect(Rect2(drill_x, 470, 34, 940), Color("e6f7f6"))
	draw_colored_polygon(PackedVector2Array([Vector2(drill_x - 36, 1410), Vector2(drill_x + 70, 1410), Vector2(drill_x + 17, 1510)]), Color("ffbd59"))
	for i in 12:
		var bx := fmod(i * 131.0 + t * 800.0, W)
		draw_circle(Vector2(bx, 1140 + (i % 5) * 120), 12, Color("8ce7e5", 0.65))

func _draw_cemetery(t: float) -> void:
	var pan := -80.0 + t * 160.0
	draw_colored_polygon(PackedVector2Array([Vector2(0, 1100), Vector2(W, 940), Vector2(W, H), Vector2(0, H)]), Color("d8edf2"))
	for i in 10:
		var x := 80.0 + i * 120.0 + pan
		var y := 980.0 + (i % 3) * 165.0
		draw_rect(Rect2(x, y, 22, 260), Color("6c452f"))
		draw_rect(Rect2(x - 50, y + 55, 122, 22), Color("6c452f"))
		draw_circle(Vector2(x + 11, y + 15), 22, Color("8d6040"))
	for i in 20:
		var sx := fmod(i * 97.0 + t * 850.0, W)
		draw_line(Vector2(sx, 500 + i * 37), Vector2(sx - 75, 530 + i * 37), Color("efffff", 0.75), 8)

func _draw_ice_problem(t: float) -> void:
	var y := 1000.0 + sin(t * TAU) * 55.0
	draw_rect(Rect2(0, y, W, H - y), Color("2c8290"))
	for i in 11:
		var x := i * 110.0
		draw_line(Vector2(x, y), Vector2(x + sin(t * TAU + i) * 70, y + 430 + (i % 3) * 120), Color("baf7f1"), 16)
	var thermo := Vector2(190, 560)
	draw_rect(Rect2(thermo.x, thermo.y, 55, 490), Color("ecf8f8"))
	draw_rect(Rect2(thermo.x + 15, thermo.y + 220 + t * 80, 25, 300 - t * 80), Color("53c8e8"))
	draw_circle(Vector2(thermo.x + 27, thermo.y + 505), 70, Color("53c8e8"))
	for i in 4:
		draw_arc(Vector2(700, 760), 170 + i * 55 + t * 40, PI * 0.1, PI * 1.6, 48, Color(1, 0.82, 0.35, 0.8 - i * 0.14), 12)

func _draw_transfer(t: float) -> void:
	var road_y := 1330.0
	draw_rect(Rect2(0, road_y, W, 590), Color("172b3b"))
	for i in 8:
		var lx := fmod(i * 220.0 - t * 1700.0, W + 220.0)
		draw_rect(Rect2(lx, road_y + 250, 120, 18), Color("f6e6a8"))
	var x := -280.0 + t * 1500.0
	draw_rect(Rect2(x, 1000, 390, 230), Color("ecf3f4"))
	draw_rect(Rect2(x + 240, 1070, 180, 160), Color("e04f5f"))
	draw_rect(Rect2(x + 70, 1080, 95, 45), Color("59a7c4"))
	draw_rect(Rect2(x + 270, 930, 40, 100), Color("ffca4e"))
	draw_circle(Vector2(x + 85, 1240), 64, Color("0a1321"))
	draw_circle(Vector2(x + 325, 1240), 64, Color("0a1321"))
	var plane_x := W + 350.0 - t * 1700.0
	draw_colored_polygon(PackedVector2Array([Vector2(plane_x - 210, 550), Vector2(plane_x + 220, 500), Vector2(plane_x - 70, 650)]), Color("c8eef4"))

func _draw_myth(t: float) -> void:
	var swap := _smooth(0.42, 0.58, t)
	var left_x: float = lerpf(80.0, -520.0, swap)
	var right_x: float = lerpf(W + 80.0, 80.0, swap)
	_card(Rect2(left_x, 520, 920, 760), Color("5b2d6f"), "MITO", "PROHIBIDO", t)
	_card(Rect2(right_x, 520, 920, 760), Color("176878"), "REALIDAD", "PERMAFROST", t + 0.4)

func _card(rect: Rect2, color: Color, title: String, word: String, t: float) -> void:
	draw_rect(rect, Color(0.02, 0.04, 0.11, 0.45), true)
	draw_rect(rect, color, false, 12)
	draw_string(font, rect.position + Vector2(0, 190), title, HORIZONTAL_ALIGNMENT_CENTER, rect.size.x, 74, Color("fff1b8"))
	draw_string(font, rect.position + Vector2(0, 390), word, HORIZONTAL_ALIGNMENT_CENTER, rect.size.x, 104, Color.WHITE)
	var p := rect.position + Vector2(rect.size.x / 2, 560)
	draw_arc(p, 95 + sin(t * TAU) * 12, 0, TAU, 48, Color("72f1d0"), 18)

func _draw_finale(t: float) -> void:
	var zoom := 1.0 - t * 0.18
	draw_set_transform(Vector2(W / 2, H / 2), 0.0, Vector2(zoom, zoom))
	var origin := Vector2(-W / 2, -H / 2)
	_mountain(PackedVector2Array([origin + Vector2(-100, 1320), origin + Vector2(260, 500), origin + Vector2(580, 1320)]), Color("173b57"))
	_mountain(PackedVector2Array([origin + Vector2(390, 1320), origin + Vector2(840, 430), origin + Vector2(1240, 1320)]), Color("20536c"))
	for i in 45:
		var x := origin.x + 80 + (i % 9) * 115.0
		var y := origin.y + 1170 + int(i / 9) * 95.0
		draw_rect(Rect2(x, y, 68, 58), Color("0c2135"))
		draw_rect(Rect2(x + 16, y + 15, 16, 20), Color("ffd667", 0.75))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	_draw_aurora(t, 310)
	for i in 3:
		draw_arc(Vector2(W / 2, 960), 410 + i * 75 + t * 80, 0, TAU, 64, Color(0.38, 0.93, 0.9, 0.22), 10)

func _draw_caption(scene: int, t: float) -> void:
	var rise: float = lerpf(70.0, 0.0, _smooth(0.08, 0.22, t))
	var alpha: float = minf(_smooth(0.04, 0.16, t), 1.0 - _smooth(0.84, 0.96, t))
	draw_rect(Rect2(55, 1450 + rise, W - 110, 300), Color(0.01, 0.025, 0.07, 0.80 * alpha), true)
	for line in 2:
		var y: float = 1565.0 + float(line) * 105.0 + rise
		draw_string(font, Vector2(80, y), CAPTIONS[scene][line], HORIZONTAL_ALIGNMENT_CENTER, W - 160, 58, Color(1, 1, 1, alpha))

func _draw_progress() -> void:
	draw_rect(Rect2(55, 1810, W - 110, 10), Color(1, 1, 1, 0.16))
	draw_rect(Rect2(55, 1810, (W - 110) * clamp(elapsed / DURATION, 0.0, 1.0), 10), Color("5ce1d1"))

func _smooth(a: float, b: float, value: float) -> float:
	return smoothstep(a, b, value)

