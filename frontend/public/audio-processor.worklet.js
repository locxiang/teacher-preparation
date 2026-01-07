// AudioWorklet 处理器 - 用于处理音频数据
// 按照科大讯飞API要求：每40ms发送1280字节（640个样本）
// 计算：16kHz采样率 * 0.04秒 = 640样本，640样本 * 2字节 = 1280字节
class AudioProcessor extends AudioWorkletProcessor {
  constructor() {
    super()
    // 按照API文档要求：每40ms发送640个样本（1280字节）
    this.bufferSize = 640
    this.buffer = new Float32Array(this.bufferSize)
    this.bufferIndex = 0
    this.processCallCount = 0
    this.totalSamplesProcessed = 0
  }

  // eslint-disable-next-line no-unused-vars
  process(inputs, _outputs) {
    this.processCallCount++
    const input = inputs[0]

    // 检查是否有输入
    if (!input || input.length === 0 || !input[0] || input[0].length === 0) {
      // 每1000次调用打印一次，避免日志过多
      if (this.processCallCount % 1000 === 0) {
        console.log(
          `[AudioWorklet] Process call ${this.processCallCount}: No input`,
        )
      }
      return true
    }

    const inputChannel = input[0]
    const frameCount = inputChannel.length
    this.totalSamplesProcessed += frameCount

    // 检查输入数据的有效性
    let hasValidData = false
    let maxInFrame = 0
    for (let i = 0; i < frameCount; i++) {
      const sample = inputChannel[i]
      const abs = Math.abs(sample)
      if (abs > maxInFrame) {
        maxInFrame = abs
      }
      if (abs > 0.0001) {
        hasValidData = true
      }
    }

    // 每1000次调用打印一次调试信息
    if (this.processCallCount % 1000 === 0) {
      console.log(
        `[AudioWorklet] Process call ${
          this.processCallCount
        }: Frames=${frameCount}, Max=${maxInFrame.toFixed(6)}, BufferIndex=${
          this.bufferIndex
        }, HasData=${hasValidData}`,
      )
    }

    // 将输入数据复制到缓冲区
    for (let i = 0; i < frameCount; i++) {
      this.buffer[this.bufferIndex++] = inputChannel[i]

      // 当缓冲区满时（达到 640 样本 = 1280字节），发送数据
      // 这对应40ms的音频数据（640样本 / 16000Hz = 0.04秒）
      if (this.bufferIndex >= this.bufferSize) {
        // 创建新的 Float32Array 以避免引用问题
        const audioData = new Float32Array(this.buffer)

        // 计算音频统计信息（用于调试）
        let maxAmplitude = 0
        let sumAmplitude = 0
        let nonZeroCount = 0
        for (let j = 0; j < audioData.length; j++) {
          const abs = Math.abs(audioData[j])
          if (abs > maxAmplitude) {
            maxAmplitude = abs
          }
          sumAmplitude += abs
          if (abs > 0.0001) {
            nonZeroCount++
          }
        }
        const avgAmplitude = sumAmplitude / audioData.length

        // 每100次发送打印一次调试信息
        const sendCount = Math.floor(
          this.totalSamplesProcessed / this.bufferSize,
        )
        if (sendCount % 100 === 0) {
          const expectedBytes = audioData.length * 2 // 16bit = 2字节/样本
          console.log(
            `[AudioWorklet] Sending buffer ${sendCount}: Samples=${
              audioData.length
            } (${expectedBytes} bytes), Max=${maxAmplitude.toFixed(
              6,
            )}, Avg=${avgAmplitude.toFixed(6)}, NonZero=${nonZeroCount}`,
          )
          console.log(
            '[AudioWorklet] Expected: 640 samples = 1280 bytes per 40ms',
          )
        }

        // 发送完整的缓冲区数据
        // 注意：postMessage 会自动序列化 Float32Array，但我们需要确保数据正确传递
        // 使用 transfer list 可以提高性能，但这里我们直接传递数组
        try {
          // 创建普通数组以确保数据正确传递（Float32Array 在序列化时可能有问题）
          const audioArray = Array.from(audioData)

          this.port.postMessage({
            type: 'audioData',
            data: audioArray, // 使用普通数组而不是 Float32Array
            maxAmplitude: maxAmplitude,
            avgAmplitude: avgAmplitude,
            sampleCount: audioData.length,
          })
        } catch (error) {
          // 如果端口已关闭，停止处理
          console.error('[AudioWorklet] Failed to post message:', error)
          return false
        }

        // 重置缓冲区索引
        this.bufferIndex = 0
      }
    }

    // 返回 true 以保持处理器运行
    return true
  }
}

registerProcessor('audio-processor', AudioProcessor)
