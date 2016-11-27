# Transmitter
  Connect to Network Emulator
  Wait for successful connection
    ## Successful
    Setup sliding window
    Start sending packets
    Foreach sent but not acked packet
      Set timer
      If timer reaches zero
        Resend packet
      If ack is received
        Mark packet as ackedA
        Move sliding window visibility
      If sliding window empty && all packets are acked
        File sent successfully

    ## Failed
    Retry up to max 3 times

# Receiver
  Connect to Network Emulator
  Wait for successful connection
    ## Successful
    Wait for incoming connection
      If sequence # == 1
        Send ACK back
      Else
        Do nothing

    ## Failed
    Retry up to max 3 times

# Network Emulator
  Wait for incoming connections
    ## Successful
    Wait for incoming packets
      Random gen true or false
      If true
        Send packet to receiver
      If false
        Do nothing with packet
