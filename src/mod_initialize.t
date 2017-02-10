!> This module handles the initialization of various components of amrvac
module mod_initialize

  implicit none
  private

  logical :: initialized_already = .false.

  ! Public methods
  public :: initialize_amrvac

contains

  !> Initialize amrvac: read par files and initialize variables
  subroutine initialize_amrvac()
    use mod_input_output
    use mod_physics, only: phys_check

    if (initialized_already) return

    ! Check whether the user has loaded a physics module
    call phys_check()

    ! Read input files
    call read_par_files()
    call initialize_vars()
    call init_comm_types()

    initialized_already = .true.
  end subroutine initialize_amrvac

  !> Initialize (and allocate) simulation and grid variables
  !> @todo Explain which ones are not initialized here
  subroutine initialize_vars
    use mod_forest
    use mod_global_parameters
    use mod_ghostcells_update

    integer :: igrid, level, ipe, ig^D
    logical :: ok
    !-----------------------------------------------------------------------------
    allocate(pw(max_blocks),pwold(max_blocks),pw1(max_blocks),pw2(max_blocks),pw3(max_blocks))
    allocate(pw4(max_blocks),pwCoarse(max_blocks),pwio(max_blocks))
    allocate(pB0_cell(max_blocks),pB0_face^D(max_blocks))
    allocate(pw_sub(max_blocks))
    allocate(px(max_blocks),pxCoarse(max_blocks),px_sub(max_blocks))
    allocate(pgeo(max_blocks),pgeoCoarse(max_blocks))
    allocate(neighbor(2,-1:1^D&,max_blocks),neighbor_child(2,0:3^D&,max_blocks))
    allocate(neighbor_type(-1:1^D&,max_blocks),neighbor_active(-1:1^D&,max_blocks))
    if (phi_ > 0) allocate(neighbor_pole(-1:1^D&,max_blocks))
    allocate(igrids(max_blocks),igrids_active(max_blocks),igrids_passive(max_blocks))
    allocate(rnode(rnodehi,max_blocks),rnode_sub(rnodehi,max_blocks),dt_grid(max_blocks))
    allocate(node(nodehi,max_blocks),node_sub(nodehi,max_blocks),phyboundblock(max_blocks))
    allocate(pflux(2,^ND,max_blocks))
    ! set time, time counter
    if(.not. restart_reset_time) then
       global_time  = zero
       it           = 0
       snapshotnext = 0
    end if

    dt=zero
    itmin=0

    ! set all dt to zero
    dt_grid(1:max_blocks)=zero

    ! check resolution
    if ({mod(ixGhi^D,2)/=0|.or.}) then
       call mpistop("mesh widths must give even number grid points")
    end if
    ixM^LL=ixG^LL^LSUBnghostcells;

    if (nbufferx^D>(ixMhi^D-ixMlo^D+1)|.or.) then
       write(unitterm,*) "nbufferx^D bigger than mesh size makes no sense."
       write(unitterm,*) "Decrease nbufferx or increase mesh size"
       call mpistop("")
    end if

    ! initialize dx arrays on finer (>1) levels
    do level=2,refine_max_level
       {dx(^D,level) = dx(^D,level-1) * half\}  ! refine ratio 2
    end do

    ! domain decomposition
    ! physical extent of a grid block at level 1, per dimension
    ^D&dg^D(1)=dx(^D,1)*dble(block_nx^D)\
    ! number of grid blocks at level 1 in simulation domain, per dimension
    ^D&ng^D(1)=nint((xprobmax^D-xprobmin^D)/dg^D(1))\
    ! total number of grid blocks at level 1
    nglev1={ng^D(1)*}

    do level=2,refine_max_level
       dg^D(level)=half*dg^D(level-1);
       ng^D(level)=ng^D(level-1)*2;
    end do

    ! check that specified stepsize correctly divides domain
    ok=({(abs(dble(ng^D(1))*dg^D(1)-(xprobmax^D-xprobmin^D))<=smalldouble)|.and.})
    if (.not.ok) then
       write(unitterm,*)"domain cannot be divided by meshes of given gridsize"
       call mpistop("domain cannot be divided by meshes of given gridsize")
    end if


    poleB=.false.
    if (.not.slab) call set_pole

    do igrid=1,max_blocks
       nullify(pwold(igrid)%w,pw(igrid)%w,pw1(igrid)%w, &
            pwCoarse(igrid)%w)
       nullify(px(igrid)%x,pxCoarse(igrid)%x)
       nullify(pgeo(igrid)%surfaceC^D,pgeo(igrid)%surface^D, &
            pgeo(igrid)%dvolume,pgeo(igrid)%dx)
       nullify(pgeoCoarse(igrid)%surfaceC^D,pgeoCoarse(igrid)%surface^D, &
            pgeoCoarse(igrid)%dvolume,pgeoCoarse(igrid)%dx)
       if (B0field) then
          nullify(pB0_cell(igrid)%w,pB0_face^D(igrid)%w)
       end if
       if (nstep>2) then
          nullify(pw2(igrid)%w)
       end if
       if (nstep>3) then
          nullify(pw3(igrid)%w)
       end if
       if (nstep>4) then
          nullify(pw4(igrid)%w)
       end if
    end do

    ! on each processor, create for later use a default patch array
    allocate(patchfalse(ixG^T))
    patchfalse(ixG^T)=.false.

    ! initialize connectivity data
    igridstail=0

    ! allocate memory for forest data structures
    allocate(level_head(refine_max_level),level_tail(refine_max_level))
    do level=1,refine_max_level
       nullify(level_head(level)%node,level_tail(level)%node)
    end do

    allocate(igrid_to_node(max_blocks,0:npe-1))
    do ipe=0,npe-1
       do igrid=1,max_blocks
          nullify(igrid_to_node(igrid,ipe)%node)
       end do
    end do

    allocate(sfc(1:3,max_blocks*npe))

    allocate(igrid_to_sfc(max_blocks))

    sfc=0
    allocate(Morton_start(0:npe-1),Morton_stop(0:npe-1))
    allocate(Morton_sub_start(0:npe-1),Morton_sub_stop(0:npe-1))

    allocate(nleafs_level(1:nlevelshi))

    allocate(coarsen(max_blocks,0:npe-1),refine(max_blocks,0:npe-1))
    coarsen=.false.
    refine=.false.
    if (nbufferx^D/=0|.or.) then
       allocate(buffer(max_blocks,0:npe-1))
       buffer=.false.
    end if
    allocate(igrid_inuse(max_blocks,0:npe-1))
    igrid_inuse=.false.

    allocate(tree_root(1:ng^D(1)))
    {do ig^DB=1,ng^DB(1)\}
    nullify(tree_root(ig^D)%node)
    {end do\}

    {#IFDEF STRETCHGRID
    logGs(1)=logG
    qsts(1)=qst
    qsts(0)=qst**2
    logGs(0)=2.d0*(qsts(0)-1.d0)/(qsts(0)+1.d0)
    if(refine_max_level>1) then
       do level=2,refine_max_level
          qsts(level)=dsqrt(qsts(level-1))
          logGs(level)=2.d0*(qsts(level)-1.d0)/(qsts(level)+1.d0) 
       end do
    end if
    }

    ! define index ranges and MPI send/receive derived datatype for ghost-cell swap
    call init_bc()
    type_send_srl=>type_send_srl_f
    type_recv_srl=>type_recv_srl_f
    type_send_r=>type_send_r_f
    type_recv_r=>type_recv_r_f
    type_send_p=>type_send_p_f
    type_recv_p=>type_recv_p_f
    call create_bc_mpi_datatype(0,nwflux+nwaux)

  end subroutine initialize_vars


end module mod_initialize
