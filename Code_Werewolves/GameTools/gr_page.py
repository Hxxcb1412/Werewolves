import gradio as gr
from .gr_functions import *
from .gr_static import *

with gr.Blocks() as demo:
    # markdown，用于展示说明文本
    gr.Markdown(value=title_text)
    state = gr.State(value=init_state())
    # 开始游戏按钮
    with gr.Row():
        start_btn = gr.Button(value="重置/开始游戏")
    with gr.Row():
        with gr.Column():
            system_text = gr.Textbox(label="系统信息展示框", value="点击 重置/开始游戏 进行游戏")
            with gr.Row():
                with gr.Column():
                    # 六个文本输入框，分别代表六个玩家，其中第一个玩家为当前玩家，其他玩家均为Agent
                    player1_text = gr.Textbox(label="Player 1 发言框",
                                              info="您的序号为Player 1，当你被投票出局之后，"
                                                   "你可以继续观战，但是你的发言将无效",
                                              interactive=True)
                    skills_btn = gr.Button(value="确定发动技能/无技能跳过（仅限夜晚可使用）")
                    player2_text = gr.Textbox(label="Player 2 发言框", interactive=False)
                    player3_text = gr.Textbox(label="Player 3 发言框", interactive=False)
                    player4_text = gr.Textbox(label="Player 4 发言框", interactive=False)
                    player5_text = gr.Textbox(label="Player 5 发言框", interactive=False)
                    player6_text = gr.Textbox(label="Player 6 发言框", interactive=False)
                    speek_btn = gr.Button(value="确定发言(即使你被淘汰了，你可以继续观战，看看自己一方到底赢了没)")
                with gr.Row():
                    # 一张图片
                    img = gr.Image(value="Source/start.jpg", interactive=False)
                with gr.Column():
                    # 六个文本输入框，分别代表六个玩家，其中第一个玩家为当前玩家，其他玩家均为Agent
                    player1_vote = gr.Dropdown(label="Player 1 指认框",
                                               info="请选择你认为是Werewolf的人，注意不要指认自己，当你被投票出局之后，"
                                                    "你可以继续观战，但是你的投票将无效",
                                               choices=["未选择" ,"Player 2", "Player 3", "Player 4", "Player 5", "Player   6"],
                                               value="未选择",
                                               interactive=True)
                    player2_vote = gr.Textbox(label="Player 2 指认框", interactive=False)
                    player3_vote = gr.Textbox(label="Player 3 指认框", interactive=False)
                    player4_vote = gr.Textbox(label="Player 4 指认框", interactive=False)
                    player5_vote = gr.Textbox(label="Player 5 指认框", interactive=False)
                    player6_vote = gr.Textbox(label="Player 6 指认框", interactive=False)
                    vote_btn = gr.Button(value="确认投票(即使你被淘汰了，你可以继续观战，看看自己一方到底赢了没)")

    start_btn.click(fn=fn_start_or_restart,
                    inputs=[],
                    outputs=[state,
                             system_text,
                             player1_text, player2_text, player3_text, player4_text, player5_text, player6_text,
                             player1_vote, player2_vote, player3_vote, player4_vote, player5_vote, player6_vote,
                             img])
    skills_btn.click(fn=fn_skills_use,
                     inputs=[state, player1_text],
                     outputs=[state,
                              system_text])
    # speek_btn.click(fn=fn_speek(),
    #                 inputs=[state, player1_text],
    #                 outputs=[state, system_text, player2_text, player3_text,
    #                          player4_text, player5_text, player6_text])
    # vote_btn.click(fn=fn_vote(),
    #                inputs=[state, player1_vote],
    #                outputs=[state,
    #                         system_text,
    #                         player1_text, player2_text, player3_text, player4_text, player5_text, player6_text,
    #                         player2_vote, player3_vote, player4_vote, player5_vote, player6_vote,
    #                         img]
    #                )