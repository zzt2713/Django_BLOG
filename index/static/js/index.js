new fullpage('#fullpage', {
            autoScrolling: true,
            scrollHorizontally: true,
            navigation:false,
       verticalCentered: false,
            afterLoad: function(origin, destination, direction) {
                // 如果是最后一页，隐藏所有箭头
                if (destination.index === 2) {
                    document.querySelectorAll('.down-arrow').forEach(arrow => {
                        arrow.style.display = 'none';
                    });
                } else {
                    document.querySelectorAll('.down-arrow').forEach(arrow => {
                        arrow.style.display = 'block';
                    });
                }
            }
        });
        var typed = new Typed('#element', {
            strings: [
                "我是银河里漂泊的音符，用歌声编织希望的网。",
                "琴弦震颤时，宇宙的风都染上温度。",
                "不做被仰望的星，只愿当掠过耳畔的歌，把勇气与温柔藏进旋律。",
                "让每个疲惫的灵魂，都能在我的节奏里，找到继续前行的力量。",
                "今夜，群星因我回响，灵魂与你相拥！",
                " 听，谐乐的低吟更加清晰了……",
                " 万事俱备，到了登台演出的时刻了。",
                " 乐曲之外的准备也不能懈怠。",
            ],
            typeSpeed: 80,
            backSpeed: 50,
            loop: true,
        });

        // 可选：添加随机气泡大小和位置（增强动态感）
        document.addEventListener('DOMContentLoaded', function() {
            const bubbles = document.querySelectorAll('.bubble');
            bubbles.forEach(bubble => {
                // 随机调整大小（±10%）
                const sizeRatio = 0.9 + Math.random() * 0.2;
                bubble.style.width = `${parseInt(bubble.style.width) * sizeRatio}px`;
                bubble.style.height = `${parseInt(bubble.style.height) * sizeRatio}px`;

                // 随机调整初始透明度
                bubble.style.opacity = 0.5 + Math.random() * 0.4;
            });
        });