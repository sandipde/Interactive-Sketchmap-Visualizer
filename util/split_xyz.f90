program convert
implicit none
integer::iat,nat,i,j,k,iframe,stat
real(8)::rxyz(3),c(9)
character(len=2)::atname
character(len=6)::fn
character(len=14)::filename
iframe=0
do while (1==1)
read(*,*,IOSTAT=stat)nat 
IF(IS_IOSTAT_END(stat)) STOP
write(fn,'(I6.6)') iframe
filename='set.'//fn//'.xyz'
open(1,file=filename)
read(*,*) 
write(1,*) nat 
write(1,*) "frame: ",iframe !'Lattice="',(c(i),i=1,9), '" Properties=species:S:1:pos:R:3'
do iat=1,nat
  read(*,*) atname,(rxyz(i),i=1,3)
  write(1,'(1a,3(2X,F5.1))') atname,(rxyz(i),i=1,3)
enddo
close(1)
iframe=iframe+1
enddo
end program convert
