# START
# HUFFMAN CODING LOGIC

import heapq
from collections import Counter
import time

class HuffmanNode :
    def __init__(self,char,freq):
        self.char=char
        self.freq=freq
        self.left=None
        self.right=None
        
    def __lt__(self,other) :
        return self.freq<other.freq
    
    def is_leaf(self) :
        return self.left is None and self.right is None

class HuffmanCoding :
    def __init__(self) :
        self.root=None
        self.codes={}
        self.reverse_codes={}
        
    def build_huffman_tree(self,text) :

        """build a Huffman Tree from input text."""
        # handle edge cases
        if not text :
            return None
            
        # count frequency of each character
        frequency=Counter(text)
        
        # handle single character case
        if len(frequency)==1 :
            char=next(iter(frequency.keys()))
            node=HuffmanNode(char,frequency[char])
            return node
        
        # create a priority queue (min heap)
        priority_queue=[HuffmanNode(char,freq) for char,freq in frequency.items()]
        heapq.heapify(priority_queue)
        
        # build the Huffman tree
        while len(priority_queue) > 1 :
            # get the two nodes with lowest frequency
            left=heapq.heappop(priority_queue)
            right=heapq.heappop(priority_queue)
            
            # create a new internal node with these two nodes as children
            # and frequency equal to the sum of their frequencies
            internal_node=HuffmanNode(None,left.freq+right.freq)
            internal_node.left=left
            internal_node.right=right
            
            # add the new node back to the queue
            heapq.heappush(priority_queue,internal_node)
        
        # the remaining node is the root of the Huffman tree
        self.root=priority_queue[0] if priority_queue else None
        return self.root
    
    def generate_codes(self,node=None,current_code="") :
        """generate Huffman codes for each character."""
        if node is None :
            node=self.root
            self.codes={}
            
        # if this is a leaf node (has a character)
        if node.char is not None :
            if current_code == "" :  # special case for single character input
                self.codes[node.char]="0"
            else :
                self.codes[node.char]=current_code
            self.reverse_codes[current_code]=node.char
        
        # traverse left (add '0' to code)
        if node.left:
            self.generate_codes(node.left,current_code+"0")
        
        # traverse right (add '1' to code)
        if node.right :
            self.generate_codes(node.right,current_code+"1")
        
        return self.codes

    def encode_text(self,text) :
        """encode text using Huffman coding."""
        if not text :
            return bytearray(), 0, ""
        
        # build Huffman tree and generate codes
        self.build_huffman_tree(text)
        self.generate_codes()
        
        # encode the text as a bit string
        encoded_bit_string="".join(self.codes[char] for char in text)
        
        # calculate padding needed
        padding=8-(len(encoded_bit_string)%8) if len(encoded_bit_string)%8!=0 else 0
        
        # add padding bits
        padded_encoded=encoded_bit_string+"0" * padding
        
        # convert to bytes
        encoded_bytes=bytearray()

        for a in range(0,len(padded_encoded),8) :
            byte=padded_encoded[a:a+8]
            encoded_bytes.append(int(byte,2))
        
        return encoded_bytes,padding,encoded_bit_string
    
    def decode_bytes(self,encoded_bytes,padding) :
        
        """decode Huffman encoded bytes back to text."""
        if not encoded_bytes:
            return ""
        
        # convert bytes back to a bit string
        bit_string=""

        for byte in encoded_bytes:
            # convert each byte to 8 bits
            bits=bin(byte)[2:].zfill(8)
            bit_string+=bits
        
        # remove padding
        if padding>0 :
            bit_string=bit_string[:-padding]
        
        # decode using the Huffman tree
        decoded_text=[]
        current_code=""
        
        for bit in bit_string :
            current_code+=bit
            if current_code in self.reverse_codes :
                decoded_text.append(self.reverse_codes[current_code])
                current_code = ""
        
        return "".join(decoded_text)
    
    def print_tree(self,node=None,prefix="",is_last=True):
        """print a text-based tree visualization."""

        if node is None :
            node=self.root
            print("\nHuffman Tree Structure :")
        
        # print the current node
        branch="└── " if is_last else "├──"  #  symbol is taken from internet i.e '├──'&'└──' for accurate hierarchy
        
        # format the node information
        if node.char is not None :
            if node.char==' ':
                node_info=f"'space': {node.freq}"
            elif node.char=='\n' :
                node_info=f"'\\n': {node.freq}"
            elif node.char=='\t' :
                node_info=f"'\\t': {node.freq}"
            elif node.char=='\r' :
                node_info=f"'\\r': {node.freq}"
            elif ord(node.char)<32 or ord(node.char) > 126 :  # non-printable characters
                node_info = f"'\\x{ord(node.char):02x}': {node.freq}"
            else :
                node_info=f"'{node.char}': {node.freq}"
        else :
            node_info=f"Internal Node : {node.freq}"
        
        print(prefix + branch + node_info)
        
        # prepare the prefix for children
        extension = "    " if is_last else "│   "
        new_prefix=prefix+extension
        
        # print right child first (will appear lower in the output)
        if node.right :
            has_left=node.left is not None
            self.print_tree(node.right,new_prefix,not has_left)
        
        # then print left child
        if node.left :
            self.print_tree(node.left,new_prefix,True)

    def print_compression_stats(self,original_text,encoded_bytes) :
        """print detailed compression statistics."""
        original_size=len(original_text)
        compressed_size=len(encoded_bytes)
        
        print("\nCompression Statistics :")
        print(f"Original size : {original_size} bytes ({original_size * 8} bits)")
        print(f"Compressed size : {compressed_size} bytes ({compressed_size * 8} bits)")
        
        if original_size>0 :
            compression_ratio=original_size/compressed_size
            compression_percentage=(original_size-compressed_size)/original_size*100
            print(f"Compression ratio : {compression_ratio:.2f}x")
            print(f"Space saved : {compression_percentage:.2f}%")
         
        else :
            print("Compression ratio : N/A (empty input)")
            
    def visualize_encoding(self,text,bit_string) :
        """visualize the encoding process in one line."""
        print("\nEncoding Visualization :")
        
        # initialize variables
        current_pos=0
        result=[]
        
        # for each character in the original text
        for char in text :
            # get the code for this character
            code=self.codes[char]
            code_len=len(code)
            
            # format the character
            if char==' ':
                char_display="'space'"
            elif char=='\n':
                char_display="'\\n'"
            elif char=='\t':
                char_display="'\\t'"
            elif char=='\r':
                char_display="'\\r'"
            elif ord(char)<32 or ord(char)>126 :  # non-printable characters
                char_display=f"'\\x{ord(char):02x}'"
            else :
                char_display=f"'{char}'"
            
            # add to result
            result.append(f"{char_display}→{code}")
            current_pos+=code_len
        
        # join all parts with arrows
        print(" | ".join(result))
        
        # show the full bit string
        print("\nFull bit string :")
        print(bit_string)
        
        # show binary grouping for bytes
        print("\nGrouped into bytes :")
        byte_groups=[]
        for a in range(0,len(bit_string),8) :
            byte=bit_string[a:a+8].ljust(8,'·')  # use dot for padding visualization
            byte_groups.append(byte)
        print(' '.join(byte_groups))



def main() :
    huffman=HuffmanCoding()
    
    print("Huffman Coding Text Compression")
    print("=" * 30)
    
    # get text input from user
    text=input("\nEnter text to compress: ")
    if not text :
        print("No input provided. Using example text instead.")
        text="this is an example for huffman encoding"
    
    print(f"\nOriginal text ({len(text)} characters) :")
    print(text[:100] + ("..." if len(text) > 100 else ""))
    
    # measure compression time
    start_time=time.time()
    
    # compress the text
    encoded_bytes,padding,bit_string=huffman.encode_text(text)
    
    compression_time=time.time()-start_time
    
    # print codes
    print("\nHuffman Codes (sorted by code length) :")
    for char,code in sorted(huffman.codes.items(),key=lambda x: (len(x[1]), x[1])):
        if char==' ':
            print(f"'space': {code}")
        elif char=='\n':
            print(f"'\\n': {code}")
        elif char=='\t':
            print(f"'\\t': {code}")
        elif char=='\r':
            print(f"'\\r': {code}")
        elif ord(char) < 32 or ord(char) > 126:  # non-printable characters
            print(f"'\\x{ord(char):02x}': {code}")
        else:
            print(f"'{char}': {code}")
    
    # visualize the encoding
    if len(text)<=20 :  # only visualize for short texts
        huffman.visualize_encoding(text,bit_string)
    else :
        # visualize just the first few characters
        sample_text=text[:10]
        sample_bit_string="".join(huffman.codes[char] for char in sample_text)
        huffman.visualize_encoding(sample_text, sample_bit_string)
        print("\n(Showing only the first 10 characters due to length)")
    
    # print compression statistics
    huffman.print_compression_stats(text,encoded_bytes)
    print(f"Compression time: {compression_time:.4f} seconds")
    
    # print tree
    huffman.print_tree()
    
    # measure decompression time
    start_time=time.time()
    
    # decompress and verify
    decoded_text=huffman.decode_bytes(encoded_bytes,padding)
    
    decompression_time=time.time()-start_time
    
    print(f"\nDecoded text ({len(decoded_text)} characters) :")
    print(decoded_text[:100]+("..." if len(decoded_text) > 100 else ""))
    print(f"Decompression time : {decompression_time:.4f} seconds")
    
    # Verification
    if text==decoded_text :
        print("\nVerification: SUCCESS - Original and decoded texts match")
    else :
        print("\nVerification: FAILED - Original and decoded texts do not match")

main()


# END