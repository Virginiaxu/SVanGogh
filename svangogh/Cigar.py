#!/usr/env python
import re
class Cigar():
	def __init__(self,cig=None):
		"""----------------------------------------------------------------"""
		"""Courtesy of Pysam:http://pysam.readthedocs.io/en/latest/api.html"""
		CODE2CIGAR= ['M','I','D','N','S','H','P','=','X','B']
		"""---------- 0   1   2   3   4   5   6   7   8   9 ---------------"""
		#if PY_MAJOR_VERSION >= 3:
			#CIGAR2CODE = dict([y, x] for x, y in enumerate(CODE2CIGAR))
		#else:
		CIGAR2CODE = dict([ord(y), x] for x, y in enumerate(CODE2CIGAR))
		CIGAR_REGEX = re.compile("(\d+)([MIDNSHP=XB])")
		parts = CIGAR_REGEX.findall(cig)
		self.cig=[(CIGAR2CODE[ord(y)], int(x)) for x,y in parts]
		"""----------------------------------------------------------------"""
		self.leftClip=False
		self.rightClip=False
		leftFlg, leftLen = self.cig[0]
		rightFlg, rightLen = self.cig[-1]
		if leftFlg == 4 or leftFlg == 5: self.leftClip=True
		if rightFlg == 4 or rightFlg == 5: self.rightClip=True
		self.qStart=None
		self.qEnd=None
	def qPos(self):
		qInd=0
		qStart=0
		for (flg,leng) in self.cig:
			if flg == 0 or flg == 1 or flg==4 or flg==5 or flg==7 or flg==8: qInd+=leng
			if (flg==0 or flg==7) and qStart==0: qStart=qInd-leng-1
		if qStart < 0 : qStart=0
		qEnd=0
		terminator=False
		for (flg,leng) in reversed(self.cig):
			if terminator==True: break
			if flg == 0 or flg == 1 or flg==4 or flg==5 or flg==7 or flg==8: qInd-=leng
			if (flg==0 or flg==7) and qEnd==0:
				qEnd=qInd+leng-1
				terminator=True
		self.qStart, self.qEnd = int(qStart), int(qEnd)
