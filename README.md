# File-Sharing-System

1. Goal and Learning Objectives

In this assignment you will have the opportunity to implement BitTrickle, a permissioned, peer-to- peer file sharing system with a centralised indexing server.  Your applications are based on both client-server and peer-to-peer models, consisting of one server and multiple clients, where:

1.   The server authenticates users who wish to join the peer-to-peer network, keeps track of which users store what files, and provides support services for users to search for files and to connect to one another and transfer those files directly.

2.   The client is a command-shell interpreter that allows a user to join the peer-to-peer network and interact with it in various ways, such as making files available to the network, and retrieving files from the network.

All  client-server  communication  must  be  over  UDP.     All  peer-to-peer   (i.e.  client-to-client) communication must be over TCP.

You will additionally submit a short report.

On completing this assignment, you will gain sufficient expertise in the following skills:

1.   A deeper understanding of both client-server and peer-to-peer architectures.
2.   Socket programming with both UDP and TCP transport-layer protocols.
3.   Designing an application layer protocol.

The assignment is worth 20% of your final grade.

2. Assignment Specification

To provide some context, a high-level example of BitTrickle’s primary file sharing functionality is shown inFigure 1. In addition to the central indexing server, there are two authenticated, active peers in the network, “A” and “B” .  The exchange of messages are:

1.   “A” informs the server that they wish to make “X.mp3” available to the network.
2.   The server responds to “A” indicating that the file has been successfully indexed.
3.   “B” queries the server where they might find “X.mp3” .
4.   The server responds to “B” indicating that “A” has a copy of “X.mp3” .
5.   “B” establishes a TCP connection with “A” and requests “X.mp3” .
6.   “A” reads “X.mp3” from disk and sends it over the established TCP connection, which “B” receives and writes to disk.

Figure 1: Sharing a file with BitTrickle

2.1. Authentication

Before a user can join the network and become an active peer, they must first authenticate with the server.  When the client is executed, it should prompt the user to enter their username and password. These  should  be  sent  to  the   server,  with  the   server  response  indicating   success  or   failure. Authentication should fail if:

•   The username is unknown; or
•   The username is known, but the password does not match; or
•   The user is currently active (see2.2. Heartbeat Mechanism).

Should authentication fail, an appropriate message should be printed, and the user should again be prompted to enter their username and password.
Should authentication succeed, the peer should become active (see 2.2. Heartbeat Mechanism) and the user may start issuing commands (see2.3. Client Commands).

The list of users authorised to join the network is stored in a credentials file.  You may assume that  during marking any username and password entered by the user will be non-blank and well formed, as per the rules of the credentials file (see2.1.1. Credentials File).

2.1.1. Credentials File

The credentials file is a text file available to the server that contains the usernames and passwords of those authorised to join the network.  This file is not available at the client.

Usernames and passwords are each limited to 16 characters and shall consist only ofprintable ASCII characters.  Each line of the credentials file contains one username-password pair, separated by a single space, with no leading or trailing whitespace, and is terminated by a single  '\n' newline character.

You may assume that each username in the credentials file will be unique, but you should not assume any particular ordering of the credentials file. You may assume that the server has sufficient 代 写COMP3331/9331 Computer Networks and Applications resources to store all credentials in main memory, should you choose to read the file once on server startup.

The credentials file will be named credentials.txt.   It will be in the working directory of the server, and it will follow the format and rules stated above.

Do not hard code any credentials within your server program. These must be read from the file when the server is executed.  Failure to do so will likely result in your applications not passing any testing.

Do not hard code any path to the credentials file, or assume any name other than credentials.txt, within your server program.  The program must read the file credentials.txt from the current working directory.  Failure to do so will likely result in your applications not passing any testing.

A sample credentials file is provided on the assignment page of the course website.   A different credentials file will be used during marking.  You may assume the file will be present in the working directory of the server, will have the same name, will have the necessary permissions, will follow the same format and rules, and will remain present and unmodified for the lifetime of the server.

Your server program is not expected to create new or alter existing accounts, and your server is not expected to modify this file in any way.

2.2. Heartbeat Mechanism

The server provides various support services to the peer-to-peer network by maintaining state as to which peers are currently active.  Consider the example in Figure 1.  When “B” queries the server where it might find “X.mp3”, the server should only direct “B” to connect to “A” if “A” is active.

To achieve this, BitTrickle utilises a “heartbeat” mechanism.  These are messages sent periodically by each client to the server to remind the server that the peer is still active.  Specifically, after being authenticated, the client should send such a message every 2 seconds.  Meanwhile, the server should only consider a peer active if, within the last 3 seconds, the user authenticated, or the server received a heartbeat from that peer.

You may assume that the 1 second difference is sufficient to account for any reasonable network and server latency.  You may also assume that heartbeat messages will be delivered reliably.

Note, the heartbeat mechanism will need to run in a separate thread of the client so that the client can concurrently accept and act upon user input (see3.2. Client Design).

2.3. Client Commands

The client, upon authenticating the user, should support the following 7 commands. As an interactive shell, the client does not need to accept further user input until the previous command has completed.

While it is good programming practice to validate all user input, you may assume that during marking all user input will be well formed.  That is, only valid commands will be entered, in lower case, and where the command takes an argument, then an argument will be given, with a single space separating the command and the argument.  The argument will also be well formed, case sensitive, and contain no internal whitespace.  Furthermore, user input will contain no leading or trailing whitespace.

2.3.1. get <filename>

The client should query the server for any active peers that have published (i.e. shared) a file with an exactly matching filename.  If there are multiple such peers, the server (or client) may select one arbitrarily.  The client should then establish a TCP connection with the peer, download the file to its working directory, and print a message indicating success.  If there are no active peers with a file that matches, then the client should print a message indicating failure.

You may assume that:

•   The file will remain published via the uploading peer until the transfer is complete.
•   The uploading peer will remain active until the transfer is complete.
•   The uploading peer will have the necessary permissions to read the file in its working directory, and the downloading peer will have the necessary permissions to create a new file in its working directory and write to it.
•   The downloading peer will have no pre-existing file in its working directory with a matching name.  By extension, the downloading peer will not have published a matching file.
•   File names are globally unique, that is, two different files will not share the same name.

Also note:

•   The uploading peer must  still be able to accept and execute user commands while any uploading is taking place.
•   Multiple clients may be downloading files from the same peer at the same time.  These files may be the same and/or different.
•   As with the heartbeat mechanism, this requires the client code to be multithreaded (see3.2. Client Design).

2.3.2. lap

The client should query the server for a list of active peers and print out their usernames.   The list should not include the peer issuing the query.  The usernames may be printed in any order.  If there are no active peers, then a suitable message should be printed.

2.3.3. lpf

The client should query the server for a list of files that are currently published (i.e. shared) by the user and print out their names.  The file names may be printed in any order.  If the user currently has no published files, then a suitable message should be printed.

Note, this is intended as a server request so that the client isn’t required to maintain any persistent state.  That is, a user can publish one or more files, go offline, and should they come back online, then any files previously published will still be listed without any need to store that information locally or re-publish.

2.3.4. pub <filename>

The client should inform. the server that the user wishes to publish a file with the given name.  This command should be idempotent, that is, executing it repeatedly with the same argument should have no additional effect.   The file should remain published until such time as it may be unpublished, regardless of whether the peer remains active. That is, a user can publish one or more files, go offline, and should they come back online, then any files previously published will still be shared without any need to re-publish.

You may assume that the file exists in the working directory of the client, with the necessary read permissions, and will remain present throughout testing.

2.3.5. sch <substring>

The client should query the server for any files published by active peers that contain the case sensitive substring within their name and print out the names of any such files.  The list should not include any files published by the user issuing the query. The file names maybe printed in any order. If there are no files published by active peers that contain the substring, then a suitable message should be printed.

2.3.6. unp <filename>

The client should inform. the server that it wishes to unpublish a file with the given name and print out a message indicating success or failure. Failure would occur if the user has no published file with a matching name.

2.3.7. xit

The client should gracefully terminate. Note, this requires no server communication. Given the client will no longer send heartbeats, the server should infer that the peer has left the network.

2.5. Application Output

We do not mandate the exact text that should be displayed by the client or the server.  However, you must make sure that the displayed text is easy to comprehend and adequately captures the behaviour of each application and their interactions.

Some examples illustrating client-server interaction are provided in H. Sample Interactions.

Please do not email course staff or post on the forum asking if your output is acceptable.  This is not scalable for a course of this size. If you are unsure of your output, then you should follow the example output.

3. Program Design Considerations

3.1. Server Design

The  server  program  should  be  less  involved  than  the  client.    Most  commands  require  simple request/response interactions over UDP between the client and server.  On the server side this can be achieved with a single thread of execution and a single socket.  The main server complexity will be in defining and utilising data structures to manage the state of the peer-to-peer network.

While we do not mandate the specifics, it is critical that you invest some time into thinking about the design of your data structures.  Examples of state information includes the time when each peer was last active (or the time it will be deemed inactive), the current address of their TCP welcoming socket, the files that are published on the network, and a list of users who have published each of those files.

As you may have learnt in your programming courses, it is not good practice to arbitrarily assume a fixed  upper  limit  on  such  data  structures.  Thus,  we  strongly  recommend  allocating  memory dynamically for all the data structures that are required.

Should you choose to implement a multithreaded server, then you should be particularly careful about how multiple threads will interact with the various data structures.

3.2. Client Design

While the client program won’t need to maintain much state, it will be more complex than the server, as it will need to manage multiple sockets and multiple threads of execution. Figure 2illustrates the sockets involved in the example of Figure 1. Each client minimally has a UDP socket to communicate with the server, and a TCP welcoming socket to listen for file download requests from other peers.

When a download takes place, in this case with client “B” requesting a file from client “A”, “B” creates a new TCP client socket and initiates a three-way handshake with the welcoming socket of “A” .  In this context, “B” can be viewed as the client and “A” as the server in a client-server model.  Once the handshake is complete, a new connection socket will be created at “A”, and the data transfer  can commence.

Figure 2: BitTrickle sockets from the example of Figure 1

Of course the peer-to-peer network may be more complex.  “A” may be managing any number of connection sockets to support multiple peers that are downloading files simultaneously.  Meanwhile “A” should be sending heartbeats periodically to the server and might also be downloading a file itself from another peer in response to a user command.   A robust way to achieve this is to use multithreading.

In this approach there could be three threads that are running for the life of the client:

1.   To accept and act upon user input.
2.   To periodically send heartbeat messages to the server via UDP.
3.   To listen for download requests via the TCP welcoming socket, and, when one is received:    a.   Launch  a  short-lived  thread  with  the  TCP  connection  socket  to perform. the  file transfer.

When the client starts up it should create a UDP socket to communicate with the server and a TCP socket to accept peer-to-peer download requests.  It could then spin off a new thread to listen for download requests on the TCP socket (thread 3 above).  The main thread (thread 1 above) could then initiate the authentication process.  At some stage the client will need to send the address of its TCP socket  to  the  server.    This  could  be  included  as  part  of  the  authentication  exchange  or  sent immediately after having successfully authenticated.   Once  successfully  authenticated, the client could spin off a new thread to periodically send heartbeat messages (thread 2 above).   The main thread (thread 1 above) could then enter its interactive shell loop, prompting the user for input and executing each command.

3.3. Application Layer Protocol

You are implementing an application layer protocol for realising the BitTrickle file sharing system. You will have to design the format (both syntax and semantics) of the messages exchanged between the participants, and the actions taken by each entity on receiving these messages. We do not mandate any specific requirements regarding the design of your application layer protocol.   We  are  only concerned with the end result, i.e. the outlined functionality of the system.  You may wish to revisit some of the application layer protocols that we have studied (HTTP, SMTP, etc.) to see examples of message format, actions taken, etc.

3.4. Message / Buffer Sizes

You may assume that the payload of UDP-based application messages (e.g. a list of active peers or a list of matching files) does not exceed 1024 bytes.  You are free to nominate appropriate buffer sizes for these messages based on the additional overhead of your application layer protocol.

You should not assume that files transferred via TCP can fit within any nominal buffer.   The uploading peer may need to repeatedly read a chunk of the file and write it to the socket, and correspondingly, the downloading peer may need to repeatedly read a chunk from the socket and write it to the file.

3.5. Name, Type, and Size of Published Files

You may assume that all files published on BitTrickle will have names no greater than 16 characters in total, consisting only of alphanumeric, dash, dot, and underscore ASCII characters. File names are case sensitive.  For example, a.txt is distinct from A.txt.  You may assume that during marking, filename and substring arguments provided as user input will follow these same rules.

You should not assume that files published on BitTrickle are of a particular format or encoding. They should be read and written in binary mode as raw bytes, rather than in text mode.

You should not assume that files published on BitTrickle are constrained to a particular size limit.

You are encouraged to use tools like diff to verify that any received file is an exact duplicate of the original.

4. Report

You should submit a small report (no more than 3 pages) named report.pdf.  This should include:

•   Details  of which  language  you  have  used  (e.g.,  C)  and  the  organisation  of your  code (Makefile, directories if any, etc.).
•   The  overall  program  design,  for  example,  the  main  components  (client,  server,  helper classes/functions) and how these components interact.
•   Data structure design, for example, any data structures used by the server to maintain state about published files and active peers.
•   Application layer protocol message format(s).
•   Known limitations, for example, if your program does not work under certain circumstances, then report those circumstances.
•   Also indicate any segments of code that you have borrowed from the Web or other sources.
